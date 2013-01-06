# Copyright (c) 2006 Jurgen Scheible
# Sound recording / playing script

import appuifw
import e32
import audio
import os


class Signal():
    def __init__(self):
        self.callbacks = []

    def reset(self):
        self.callbacks = []

    def emit(self, *args, **kwarg):
        for callback in self.callbacks:
            callback(*args, **kwarg)

    def connect(self, callback):
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def disconnect(self, callback):
        if callback in self.callbacks:
            self.callbacks.remove(callback)


def loaded_state_required(method):
    def decorated(self, *args, **kwarg):
        if self.state == AudioPlayer.UNLOADED:
            raise Exception("No audio file is loaded")
        return method(self, *args, **kwarg)

    return decorated


class AudioPlayer():
    """docstring for AudioPlayer"""
    UNLOADED = u'UNLOADED'
    PLAYING = u'PLAYING'
    STOPPED = u'STOPPED'
    PAUSED = u'PAUSED'

    def __init__(self):
        self.filename = ""
        self.music = None

        self.state = self.UNLOADED
        self.begin = 0
        self.end = 0
        self.position = 0
        self.timer = e32.Ao_timer()

        self.is_waiting = False
        self.lock = e32.Ao_lock()

        self.state_changed = Signal()
        self.position_changed = Signal()

    def __del__(self):
        self.unload()

    def reset(self):
        self.unload()
        self.state_changed.reset()
        self.position_changed.reset()

    def load(self, filename):
        self.unload()
        self.music = audio.Sound.open(filename)
        if self.music.state == audio.ENotReady:
            self.music = None
            raise Exception("Failed to open audio file ")
        self.filename = filename
        self._change_to_state(self.STOPPED)
        self.begin = 0
        self.end = self.duration()

    def unload(self):
        if self.state == self.UNLOADED:
            return

        self.stop()
        self.music.close()
        self.music = None
        self.filename = ""
        self.begin = 0
        self.end = 0
        self._change_to_state(self.UNLOADED)

    @loaded_state_required
    def play(self):
        if self.state != self.STOPPED:
            self.stop()

        self._start_from(self.begin)

    @loaded_state_required
    def stop(self):
        if self.state != AudioPlayer.STOPPED:
            self.music.stop()

        self._set_stop()

    @loaded_state_required
    def pause(self):
        if self.state in (self.STOPPED, self.PAUSED):
            return

        self.timer.cancel()
        self.music.stop()
        self._change_to_state(self.PAUSED)

    @loaded_state_required
    def resume(self):
        if self.state == self.PLAYING:
            return
        self._start_from(self.position)

    @loaded_state_required
    def seek(self, target):
        target = max(self.begin, target)
        target = min(self.end, target)

        self.position = target
        self.music.set_position(target * 1000)

    @loaded_state_required
    def wait(self):
        if self.state == self.STOPPED:
            return

        if not self.is_waiting:
            self.is_waiting = True
            self.lock.wait()

    @loaded_state_required
    def duration(self):
        return self._to_ms(self.music.duration())

    @loaded_state_required
    def set_begin(self, begin):
        if begin >= 0 and begin < self.end:
            self.begin = begin

    @loaded_state_required
    def set_end(self, end):
        if end <= self.duration() and end > self.begin:
            self.end = end

        if self.end < self.duration():
            self.position_changed.connect(self._check_end)
        else:
            self.position_changed.disconnect(self._check_end)

    @loaded_state_required
    def set_clip(self, begin, end):
        if (begin >= 0 and
                end <= self.duration() and
                end > begin):
            self.clr_clip()
            self.set_begin(begin)
            self.set_end(end)

    @loaded_state_required
    def clr_clip(self):
        if self.state == self.UNLOADED:
            raise Exception("No audio file is loaded")

        self.set_begin(0)
        self.set_end(self.duration())

    def _start_from(self, position=0):
        self.position = position
        if self.position:
            self.music.set_position(self.position * 1000)
        self.music.play(callback=self._cb_start_stop)
        self._change_to_state(self.PLAYING)
        self.timer.cancel()
        self.timer.after(0.1, self._cb_interval)

    def _set_stop(self):
        self.timer.cancel()
        self.position = self.end
        if self.is_waiting:
            self.lock.signal()
            self.is_waiting = False
        self._change_to_state(self.STOPPED)

    def _cb_interval(self):
        self.position = self._to_ms(self.music.current_position())
        self.position_changed.emit(self.position)

        self.timer.cancel()
        if self.state == self.PLAYING:
            self.timer.after(0.1, self._cb_interval)

    def _cb_start_stop(self, prev, curr, err):
        if curr == audio.EOpen:
            self._set_stop()

    def _change_to_state(self, next_state):
        if next_state != self.state:
            old_state = self.state
            self.state = next_state
            self.state_changed.emit(old_state, self.state)

    def _check_end(self, position):
        if (position >= self.end and
                self.state == self.PLAYING):
            print 'Reach end'
            self.stop()

    @staticmethod
    def _to_ms(position):
        return round(position / 1000)


class AudioRecorder():
    NO_MEDIA = u'NO_MEDIA'
    RECORDING = u'RECORDING'
    STOPPED = u'STOPPED'
    PLAYING = u'PLAYING'

    def __init__(self):
        self.state = self.NO_MEDIA
        self.audio = None
        self.audio_file = u"c:\\test_rec.wav"

        self.lock = e32.Ao_lock()
        self._is_waiting = False

    def __del__(self):
        if self.audio:
            self.audio.stop()
            self.audio.close()

    def new(self):
        if self.audio:
            self.audio.stop()
            self.audio.close()

        if os.path.isfile(self.audio_file):
            os.remove(self.audio_file)

        self.audio = audio.Sound.open(self.audio_file)
        if self.audio.state() != audio.EOpen:
            raise Exception('Failed to create file')

        self.state = self.STOPPED

    def record(self):
        self.audio.record()
        self.state = self.RECORDING

    def stop(self):
        self.audio.stop()
        self.audio.close()
        self.audio = audio.Sound.open(self.audio_file)
        self.state = self.STOPPED

    def _cb_start_stop(self, prev, cur, err):
        if cur == audio.EOpen:
            if self._is_waiting:
                self.lock.signal()
                self._is_waiting = False
            self.state = self.STOPPED

    def play(self):
        self.audio.play(callback=self._cb_start_stop)
        self.state = self.PLAYING

    def wait(self):
        if self.state != self.PLAYING:
            return

        if self._is_waiting:
            return

        self._is_waiting = True
        self.lock.wait()

    def duration(self):
        return self._to_ms(self.audio.duration())

    def position(self):
        return self._to_ms(self.audio.current_position())

    @staticmethod
    def _to_ms(position):
        return round(position / 1000)


import unittest


class AudioPlayerTest(unittest.TestCase):
    def setUp(self):
        self.player = AudioPlayer()
        self.audio = "c:\\ep.m4a"
        self.audio2 = "c:\\nce2.mp3"

    def test_initial_state_should_be_unloaded(self):
        self.assertEqual(self.player.state, AudioPlayer.UNLOADED)

    def test_load_should_success_when_unloaded(self):
        self.player.load(self.audio)
        self.assertEqual(self.player.state, AudioPlayer.STOPPED)
        self.assertEqual(self.player.filename, self.audio)

    def test_load_should_success_when_stopped(self):
        self.player.load(self.audio)
        self.player.load(self.audio2)
        self.assertEqual(self.player.filename, self.audio2)
        self.assertEqual(self.player.state, AudioPlayer.STOPPED)

    def test_unload_should_sucess_when_stopped(self):
        self.player.load(self.audio)
        self.player.unload()
        self.assertEqual(self.player.state, AudioPlayer.UNLOADED)
        self.assertEqual(self.player.filename, "")

    def test_unload_should_do_nothing_when_unloaded(self):
        self.player.unload()
        self.assertEqual(self.player.state, AudioPlayer.UNLOADED)

    def test_unload_should_succeed_when_playing(self):
        self.player.load(self.audio)
        self.player.play()
        self.player.unload()
        self.assertEqual(self.player.state, AudioPlayer.UNLOADED)

    def test_unload_should_succeed_when_paused(self):
        self.player.load(self.audio)
        self.player.play()
        self.player.pause()
        self.player.unload()
        self.assertEqual(self.player.state, AudioPlayer.UNLOADED)

    def test_play_should_succeed_when_stopped(self):
        self.player.load(self.audio)
        self.player.play()
        self.assertEqual(self.player.state, AudioPlayer.PLAYING)

    def test_play_should_fail_when_unloaded(self):
        self.assertRaises(Exception, self.player.play)

    def test_play_should_restart_when_playing(self):
        self.player.load(self.audio)
        self.player.play()
        self._wait(2)
        self.player.play()
        self._assert_almost_same_time(0, self.player.position)

    def test_stop_should_succeed_when_playing(self):
        self.player.load(self.audio)
        self.player.play()
        self.player.stop()
        self.assertEqual(self.player.state, AudioPlayer.STOPPED)

    def test_stop_should_succeed_when_paused(self):
        self.player.load(self.audio)
        self.player.play()
        self.player.pause()
        self.player.stop()
        self.assertEqual(self.player.state, AudioPlayer.STOPPED)

    def test_stop_should_succeed_when_stopped(self):
        self.player.load(self.audio)
        self.player.stop()
        self.assertEqual(self.player.state, AudioPlayer.STOPPED)

    def test_pause_should_succeed_when_playing(self):
        self.player.load(self.audio)
        self.player.play()
        self.player.pause()
        self.assertEqual(self.player.state, AudioPlayer.PAUSED)

    def test_pause_should_do_nothing_when_stopped(self):
        self.player.load(self.audio)
        self.player.pause()
        self.assertEqual(self.player.state, AudioPlayer.STOPPED)

    def test_pause_should_do_nothing_when_already_paused(self):
        self.player.load(self.audio)
        self.player.play()
        self.player.pause()
        self.player.pause()
        self._assert_state(AudioPlayer.PAUSED)

    def test_resume_should_continue_from_paused_position(self):
        self.player.load(self.audio)
        self.player.play()
        self._wait(1)
        self.player.pause()
        paused_position = self.player.position
        self.player.resume()
        self._assert_position(paused_position)

    def test_position_should_be_notified_when_playing(self):
        self.player.load(self.audio)
        self.position_now = 0

        def on_pos(pos):
            self.position_now = pos

        self.player.position_changed.connect(on_pos)
        self.player.play()
        self._wait(1)
        self._assert_position(self.position_now)

    def test_seek_should_be_supported(self):
        self.player.load(self.audio)
        self.player.play()
        self.player.seek(3000)
        self.player.pause()
        self._assert_position(3000)

    def test_clip_should_be_able_to_play(self):
        self.player.load(self.audio)
        self.player.set_clip(3000, 4000)
        self.player.play()
        self._assert_position(3000)
        self.player.wait()
        self._assert_position(4000)
        self._assert_state(AudioPlayer.STOPPED)

    def test_clip_should_be_kept_until_cleared(self):
        self.player.load(self.audio)
        self.player.set_clip(3000, 4000)
        self.player.play()
        self.player.wait()
        self.assertEqual(self.player.begin, 3000)
        self.assertEqual(self.player.end, 4000)
        self.player.clr_clip()
        self.assertEqual(self.player.begin, 0)
        self.assertEqual(self.player.end, self.player.duration())

    def test_pause_should_work_when_playing_a_clip(self):
        self.player.load(self.audio)
        self.player.set_clip(3000, 4000)
        self.player.play()
        self.player.pause()
        self._assert_state(AudioPlayer.PAUSED)
        self._assert_position(3000)

    def _assert_state(self, state):
        self.assertEqual(self.player.state, state)

    def _assert_almost_same_time(self, position1, position2):
        self.assertTrue(abs(position1 - position2) < 200, str(position1) + ', ' + str(position2))

    def _assert_position(self, position):
        self._assert_almost_same_time(self.player.position, position)

    def _wait(self, sec):
        e32.ao_sleep(sec)

    def tearDown(self):
        self.player.reset()
        del(self.player)


class AudioRecorderTest(unittest.TestCase):
    def setUp(self):
        self.recorder = AudioRecorder()

    def test_recorder_should_be_not_ready_at_first(self):
        self._assert_state(AudioRecorder.NO_MEDIA)

    def test_new_should_prepare_a_new_record(self):
        self.recorder.new()
        self._assert_state(AudioRecorder.STOPPED)

    def test_recorder_should_work(self):
        self.recorder.new()
        self.recorder.record()
        self._assert_state(AudioRecorder.RECORDING)
        self._wait(2)
        self.recorder.stop()
        self._assert_state(AudioRecorder.STOPPED)
        self.assertTrue(self.recorder.duration() > 0)

    def test_record_should_continue_from_last_stopped(self):
        self.recorder.new()
        self.recorder.record()
        self._wait(2)
        self.recorder.stop()
        first_duration = self.recorder.duration()
        self.recorder.record()
        self.recorder.stop()
        self._assert_almost_same_duration(first_duration)

    def test_new_should_restart_recording(self):
        self.recorder.new()
        self.recorder.record()
        self._wait(2)
        self.recorder.stop()
        self.recorder.new()
        self._assert_almost_same_duration(0)

    def test_record_should_be_able_to_play(self):
        self.recorder.new()
        self.recorder.record()
        self._wait(2)
        self.recorder.stop()
        self.recorder.play()
        self._assert_state(AudioRecorder.PLAYING)
        self.recorder.stop()
        self._assert_state(AudioRecorder.STOPPED)

    def test_wait_should_return_until_end(self):
        self.recorder.new()
        self.recorder.record()
        self._wait(2)
        self.recorder.stop()
        self.recorder.play()
        self.recorder.wait()
        self._assert_state(AudioRecorder.STOPPED)

    def tearDown(self):
        del(self.recorder)

    def _assert_state(self, state):
        self.assertEqual(self.recorder.state, state)

    def _assert_almost_same_duration(self, duration):
        self.assertTrue(abs(self.recorder.duration() - duration) < 257, str(self.recorder.duration()) + ', ' + str(duration))

    def _wait(self, sec):
        e32.ao_sleep(sec)


class HiRepeater():
    PLAY_UNLOAD = u'UNLOADED'
    PLAY_STOPPED = u'STOPPED'
    PLAY_PLAYING = u'PLAYING'
    A_SET = u'A_SET'
    AB_SET = u'AB_SET'
    AB_CANCEL = u'AB_CANCEL'

    def __init__(self):
        self.player = AudioPlayer()
        self.recorder = AudioRecorder()
        self.point_a = -1
        self.point_b = -1
        self.play_state = self.PLAY_UNLOAD

    def load(self, filename):
        self.player.load(filename)
        self.play_state = self.PLAY_STOPPED

    def play(self):
        self.player.play()
        self.play_state = self.PLAY_PLAYING

    def set_ab(self):
        if self.ab_state() in (self.AB_CANCEL, self.AB_SET):
            self.point_a = self.player.position
            self.point_b = -1
            self.player.clr_clip()
            self.player.set_begin(self.point_a)
        else:
            self.point_b = self.player.position
            self.player.set_end(self.point_b)

    def cancel_ab(self):
        self.point_a = -1
        self.point_b = -1
        self.player.clr_clip()

    def ab_state(self):
        assert(not(self.point_a < 0 and self.point_b > 0))

        if self.point_a >= 0 and self.point_b < 0:
            return self.A_SET
        if self.point_a >= 0 and self.point_b >= 0:
            return self.AB_SET
        if self.point_a < 0 and self.point_b < 0:
            return self.AB_CANCEL

    def wait(self):
        self.player.wait()

    def position(self):
        return self.player.position


class HiRepeaterTest(unittest.TestCase):
    def _wait(self, sec):
        e32.ao_sleep(sec)

    def setUp(self):
        self.repeater = HiRepeater()
        self.audio = u'c:\\nce2.mp3'
        self.repeater.load(self.audio)

    def test_load(self):
        self._assert_play_state(HiRepeater.PLAY_STOPPED)

    def _est_play(self):
        self.repeater.play()
        self._assert_play_state(HiRepeater.PLAY_PLAYING)

    def test_set_ab(self):
        self.repeater.play()
        self.repeater.set_ab()
        self._assert_ab_state(HiRepeater.A_SET)
        self.repeater.set_ab()
        self._assert_ab_state(HiRepeater.AB_SET)
        self.repeater.set_ab()
        self._assert_ab_state(HiRepeater.A_SET)
        self.repeater.cancel_ab()
        self._assert_ab_state(HiRepeater.AB_CANCEL)

    def test_repeat(self):
        self.repeater.play()
        self._wait(2)

        self._print_ab()

        a = self.repeater.position()
        self.repeater.set_ab()

        self._print_ab()

        self._wait(3)
        self.repeater.set_ab()

        self._print_ab()

        b = self.repeater.position()
        self.repeater.wait()
        self.repeater.play()
        self._assert_play_position(a)
        self.repeater.wait()
        self._assert_play_position(b)

    def _print_ab(self):
        print 'A: ', self.repeater.point_a
        print 'B: ', self.repeater.point_b

    def _assert_ab_state(self, ab_state):
        self.assertEqual(self.repeater.ab_state(), ab_state, str(self.repeater.point_a) + ':' + str(self.repeater.point_b))

    def _assert_play_state(self, play_state):
        self.assertEqual(self.repeater.play_state, play_state)

    def _assert_play_position(self, play_position):
        self.assertEqual(self.repeater.position(), play_position, str(self.repeater.point_a) + ':' + str(self.repeater.point_b))



    def tearDown(self):
        del(self.repeater)


def test_main():
    test_cases = (
        HiRepeaterTest,
        # AudioPlayerTest,
        # AudioRecorderTest,
    )
    suites = []
    load = unittest.TestLoader().loadTestsFromTestCase
    for case in test_cases:
        suites.append(load(case))
    unittest.TextTestRunner().run(unittest.TestSuite(suites))


if __name__ == '__main__':
    test_main()
