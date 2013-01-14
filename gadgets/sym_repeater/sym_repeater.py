# Copyright (c) 2006 Jurgen Scheible
# Sound recording / playing script

import appuifw
import e32
import audio
import os
import unittest
import logging


logger = logging.getLogger("HIREPEATER")
log_file_handler = logging.FileHandler('c:\\hirepeater.txt', mode='w')
log_formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s')
log_file_handler.setFormatter(log_formatter)
logger.addHandler(log_file_handler)
logger.setLevel(logging.DEBUG)


def log(message):
    logger.debug(message)


def wait(sec):
    e32.ao_sleep(sec)


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


#TODO:


class Time():
    """Represents the time"""
    def __init__(self, microseconds=0):
        self.microseconds = microseconds

    def __eq__(self, other):
        if abs(self.microseconds - other.microseconds) < 300000:
            return True
        else:
            return False

    def __add__(self, other):
        return Time(self.microseconds + other.microseconds)

    def __sub__(self, other):
        return Time(self.microseconds - other.microseconds)

    def __neg__(self):
        return Time(-self.microseconds)

    def __cmp__(self, other):
        return self.microseconds > other.microseconds

    def to_microseconds(self):
        return self.microseconds

    def __repr__(self):
        return unicode(self.microseconds)

    def __lt__(self, other):
        return self.microseconds < other.microseconds

    @staticmethod
    def sec(seconds):
        return Time(seconds * 1000 * 1000)

    def greater(t1, t2):
        return t1 if t1 > t2 else t2

    def less(t1, t2):
        return t2 if t1 > t2 else t1


class Player():
    IDLE = u'IDLE'
    READY = u'READY'
    PLAYING = u'PLAYING'
    PAUSED = u'PAUSED'

    def __init__(self):
        # Basic Management and Playback control
        log("Initializing player")
        self.filename = u''
        self.sound = None

        # Pause
        self.paused_position = None

        # AB Repeat
        self.point_a = None
        self.point_b = None

    def __del__(self):
        log("Deleting player")
        self.unload()

    def state(self):
        if not self.sound:
            return self.IDLE

        if self.sound.state() == audio.EOpen:
            if self.paused_position is None:
                return self.READY
            else:
                return self.PAUSED

        if self.sound.state() == audio.EPlaying:
            return self.PLAYING

    def load(self, filename):
        self.unload()

        if not os.path.isfile(filename):
            raise PlayerException('File Not Exist')

        log("Sound.open(%s)" % filename)
        sound = audio.Sound.open(filename)
        if sound.state() != audio.EOpen:
            raise PlayerException('File Open Error')

        self.sound = sound
        self.filename = filename

    def unload(self):
        if self.state() == self.IDLE:
            return

        self.stop()

        log("Sound.close()")
        self.sound.close()
        self.filename = u''
        self.sound = None

    def play(self):
        if self.state() in (self.IDLE, self.PLAYING):
            return

        if self.state() == self.PAUSED:
            self._restore_paused_position()

        log("Sound.play()")
        self.sound.play()

    def stop(self):
        if self.state() in (self.IDLE, self. READY):
            return

        self.paused_position = None
        log("Sound.stop()")
        self.sound.stop()

    def position(self):
        if self.state() == self.PLAYING:
            return self._sound_position()
        elif self.state() == self.PAUSED:
            return self.paused_position
        else:
            return Time(0)

    def duration(self):
        return Time(self.sound.duration())

    def _sound_position(self):
        return Time.less(Time(self.sound.current_position()), self.duration())

    def pause(self):
        if self.state() in (self.READY, self.IDLE, self.PAUSED):
            return

        self.paused_position = self.position()
        self.sound.stop()

    def _restore_paused_position(self):
        self._forward_sound_position(self.paused_position)
        self.paused_position = None

    def forward(self, offset):
        if self.state() == self.IDLE:
            return

        target = self._position_plus_offset(offset)

        if self.state() in (self.PAUSED, self.READY):
            self.paused_position = target

        if self.state() == self.PLAYING:
            self._do_forward(target)

    def backward(self, offset):
        if self.state() in (self.READY, self.IDLE):
            return

        target = self._position_minus_offset(offset)

        if self.state() == self.PAUSED:
            self.paused_position = target

        if self.state() == self.PLAYING:
            self._do_backward(target)

    def _do_forward(self, target):
        self._forward_sound_position(target - self.position())

    def _do_backward(self, target):
        self.sound.stop()
        self._forward_sound_position(target)
        self.sound.play()

    def _position_plus_offset(self, offset):
        return Time.less(self.position() + offset, self.duration())

    def _position_minus_offset(self, offset):
        return Time.greater(Time(0), self.position() - offset)

    def _forward_sound_position(self, position):
        log("Sound.set_position(%d)" % position.to_microseconds())
        self.sound.set_position(position.to_microseconds())

    def set_ab(self):
        if self.point_a and self.point_b:
            return

        elif self.point_a is None:
            self.point_a = self.position()
        else:
            self.point_b = self.position()
            self.pause()

    def cancel_ab(self):
        self.point_a = None
        self.point_b = None

    def repeat(self):
        self.stop()
        self.forward(self.point_a)
        self.play()

    def wait_stop(self):
        while (self.state() == self.PLAYING and
                self.position() < self.point_b):
            e32.ao_sleep(0.2)
        self.pause()


class PlayerException(Exception):
    pass


class PlayerTest(unittest.TestCase):
    def setup_idle(self):
        self.player = Player()

    def setup_ready(self):
        self.setup_idle()
        self.player.load(u'c:\\nce2.mp3')

    def setup_playing(self):
        self.setup_ready()
        self.player.play()

    def setup_paused(self):
        self.setup_playing()
        wait(2)
        self.paused_position = self.player.position()
        self.player.pause()

    def _assert_filename(self, filename):
        self.assertEqual(self.player.filename, filename)

    def _assert_state(self, state):
        self.assertEqual(self.player.state(), state)

    def _assert_position(self, position):
        self.assertEqual(self.player.position(), position)

    def tearDown(self):
        del(self.player)


class PlayerInIdleTest(PlayerTest):
    def setUp(self):
        self.setup_idle()

    def test_initial_state(self):
        self._assert_state(Player.IDLE)

    def test_load(self):
        test_audio = u'c:\\nce2.mp3'
        self.player.load(test_audio)
        self.assertEqual(self.player.filename, test_audio)
        self._assert_state(Player.READY)

    def test_load_a_non_existing_file(self):
        non_existing = u'c:\\non_existing.mp3'
        self.assertRaises(PlayerException, self.player.load, non_existing)
        self._assert_state(Player.IDLE)

    def test_unload(self):
        self.player.unload()
        self._assert_state(Player.IDLE)

    def test_play(self):
        self.player.play()
        self._assert_state(Player.IDLE)

    def test_stop(self):
        self.player.stop()
        self._assert_state(Player.IDLE)

    def test_pause(self):
        self.player.pause()
        self._assert_state(Player.IDLE)


class PlayerInReadyTest(PlayerTest):
    def setUp(self):
        self.setup_ready()

    def test_load(self):
        test_audio2 = u'c:\\ep.m4a'
        self.player.load(test_audio2)
        self._assert_state(Player.READY)
        self._assert_filename(test_audio2)

    def test_unload(self):
        self.player.unload()
        self._assert_state(Player.IDLE)

    def test_play(self):
        self.player.play()
        self._assert_state(Player.PLAYING)

    def test_stop(self):
        self.player.stop()
        self._assert_state(Player.READY)

    def test_pause(self):
        self.player.pause()
        self._assert_state(Player.READY)


class PlayerInPlayingTest(PlayerTest):
    def setUp(self):
        self.setup_playing()

    def test_load(self):
        test_audio2 = u'c:\\ep.m4a'
        self.player.load(test_audio2)
        self._assert_state(Player.READY)
        self._assert_filename(test_audio2)

    def test_pause(self):
        wait(1)
        position_before_pause = self.player.position()
        self.player.pause()
        self._assert_state(Player.PAUSED)
        wait(1)
        self._assert_position(position_before_pause)

    def test_unload(self):
        self.player.unload()

    def test_play(self):
        wait(1)
        position = self.player.position()
        self.player.play()
        self._assert_state(Player.PLAYING)
        self._assert_position(position)

    def test_stop(self):
        self.player.stop()
        self._assert_state(Player.READY)


class PlayerInPausedTest(PlayerTest):
    def setUp(self):
        self.setup_paused()

    def test_play(self):
        self.player.play()
        self._assert_position(self.paused_position)
        self._assert_state(Player.PLAYING)

    def test_stop(self):
        self.player.stop()
        self._assert_state(Player.READY)
        self._assert_position(Time(0))

    def test_pause(self):
        self.player.pause()
        self._assert_state(Player.PAUSED)

    def test_unload(self):
        self.player.unload()
        self._assert_state(Player.IDLE)

    def test_load(self):
        test_audio2 = u'c:\\ep.m4a'
        self.player.load(test_audio2)
        self._assert_filename(test_audio2)
        self._assert_state(Player.READY)
        self._assert_position(Time(0))


class PlayerSeekInPlayingTest(PlayerTest):
    def setUp(self):
        self.setup_playing()
        wait(2)
        self.position_before_seek = self.player.position()

    def test_forward_within_duration(self):
        offset = Time.sec(1)
        self.player.forward(offset)
        self._assert_position(self.position_before_seek + offset)

    def test_backward_within_duration(self):
        offset = Time.sec(1)
        self.player.backward(offset)
        self._assert_position(self.position_before_seek - offset)

    def test_forward_too_much(self):
        offset = Time.sec(10)
        self.player.forward(offset)
        self._assert_position(self.player.duration())

    def test_backward_too_much(self):
        offset = Time.sec(10)
        self.player.backward(offset)
        self._assert_position(Time(0))


class PlayerSeekInPausedTest(PlayerTest):
    def setUp(self):
        self.setup_paused()
        self.position_before_seek = self.player.position()

    def test_forward_within_duration(self):
        offset = Time.sec(1)
        self.player.forward(offset)
        self._assert_state(Player.PAUSED)
        self._assert_position(self.position_before_seek + offset)

    def test_backward_within_duration(self):
        offset = Time.sec(1)
        self.player.backward(offset)
        self._assert_state(Player.PAUSED)
        self._assert_position(self.position_before_seek - offset)

    def test_forward_too_much(self):
        offset = Time.sec(10)
        self.player.forward(offset)
        self._assert_state(Player.PAUSED)
        self._assert_position(self.player.duration())

    def test_backward_too_much(self):
        offset = Time.sec(10)
        self.player.backward(offset)
        self._assert_state(Player.PAUSED)
        self._assert_position(Time(0))


class PlayerSeekInReadyTest(PlayerTest):
    def setUp(self):
        self.setup_ready()

    def test_forward_within_duration(self):
        offset = Time.sec(1)
        self.player.forward(offset)
        self._assert_position(offset)
        self._assert_state(Player.PAUSED)

    def test_forward_too_much(self):
        offset = Time.sec(10)
        self.player.forward(offset)
        self._assert_state(Player.PAUSED)
        self._assert_position(self.player.duration())

    def test_backward(self):
        offset = Time.sec(1)
        self.player.backward(offset)
        self._assert_state(Player.READY)


class PlayerSeekInIdleTest(PlayerTest):
    def setUp(self):
        self.setup_idle()

    def test_forward(self):
        offset = Time.sec(1)
        self.player.forward(offset)
        self._assert_state(Player.IDLE)

    def test_backward(self):
        offset = Time.sec(1)
        self.player.backward(offset)
        self._assert_state(Player.IDLE)


class PlayerABRepeatTest(PlayerTest):
    def _assert_point_a(self, position):
        self.assertEqual(self.player.point_a, position)

    def _assert_point_b(self, position):
        self.assertEqual(self.player.point_b, position)


class PlayerABRepeatInPlayingAndABSetTest(PlayerABRepeatTest):
    def setUp(self):
        self.setup_playing()
        wait(2)
        self.point_a = self.player.position()
        self.player.set_ab()
        wait(2)
        self.point_b = self.player.position()
        self.player.set_ab()

    def test_set_point_again(self):
        self.player.set_ab()
        self._assert_point_a(self.point_a)
        self._assert_point_b(self.point_b)

    def test_repeat_begin_from_point_a(self):
        self.player.repeat()
        self._assert_position(self.point_a)

    def test_repeat_end_at_point_b(self):
        self.player.repeat()
        self.player.wait_stop()
        self._assert_state(Player.PAUSED)
        self._assert_position(self.point_b)

    def test_cancel_ab(self):
        self.player.cancel_ab()
        self._assert_point_a(None)
        self._assert_point_b(None)
        self._assert_state(Player.PAUSED)
        self._assert_position(self.point_b)


class PlayerABRepeatInPlayingAndASetTest(PlayerABRepeatTest):
    def setUp(self):
        self.setup_playing()
        wait(1)
        self.point_a = self.player.position()
        self.player.set_ab()

    def test_set_point(self):
        wait(1)
        pos = self.player.position()
        self.player.set_ab()
        self._assert_point_b(pos)
        self._assert_state(Player.PAUSED)

    def test_cancel_point(self):
        pos_at_cancel = self.player.position()
        self.player.cancel_ab()
        self._assert_point_a(None)
        self._assert_point_b(None)
        self._assert_state(Player.PLAYING)
        self._assert_position(pos_at_cancel)


class PlayerABRepeatInPlayingNoABSetTest(PlayerABRepeatTest):
    def setUp(self):
        self.setup_playing()

    def test_state(self):
        self._assert_state(Player.PLAYING)
        self._assert_point_a(None)
        self._assert_point_b(None)

    def test_set_point(self):
        wait(1)
        pos = self.player.position()
        self.player.set_ab()
        self._assert_point_a(pos)
        self._assert_state(Player.PLAYING)


class AudioRecorder():
    NO_MEDIA = u'NO_MEDIA'
    RECORDING = u'RECORDING'
    STOPPED = u'STOPPED'
    PLAYING = u'PLAYING'

    def __init__(self):
        self.state = self.NO_MEDIA
        self.audio = None
        self.audio_file = u"c:\\repeater\\record.wav"

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


class AudioRecorderTest(unittest.TestCase):
    def setUp(self):
        self.recorder = AudioRecorder()

    def test_recorder_should_be_idle_at_first(self):
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


def test_main(test_cases):
    suites = []
    load = unittest.TestLoader().loadTestsFromTestCase
    for case in test_cases:
        suites.append(load(case))
    unittest.TextTestRunner().run(unittest.TestSuite(suites))


def do_test():
    test_cases = (
        # PlayerInIdleTest,
        # PlayerInReadyTest,
        # PlayerInPlayingTest,
        # PlayerInPausedTest,
        # PlayerSeekInPlayingTest,
        # PlayerSeekInPausedTest,
        # PlayerSeekInReadyTest,
        # PlayerSeekInIdleTest,
        # PlayerABRepeatInPlayingNoABSetTest,
        # PlayerABRepeatInPlayingAndASetTest,
        # PlayerABRepeatInPlayingAndABSetTest,
        # AudioRecorderTest,
    )
    log("")
    test_main(test_cases)


class Menu():
    def __init__(self, title=u"Menu", items=None):
        self.items = [] if items is None else items
        self.title = unicode(title)

    def append_item(self, item):
        self.items.append(item)

    def append_items(self, items):
        for item in items:
            self.items.append(item)

    def item_titles(self):
        return (item[0] for item in self.items)

    def popup(self):
        item_titles = [item[0] for item in self.items]
        title = self.title

        index = appuifw.popup_menu(item_titles, title)
        return self.items[index][1]


class Repeater():
    def __init__(self):
        self.player = Player()
        self.recorder = AudioRecorder()

        self.exit_flag = False

    def compare(self):
        self.player.repeat()
        self.player.wait_stop()
        self.recorder.play()
        self.recorder.wait()

    def run(self):
        while not self.exit_flag:
            menu = self.make_menu()
            action = menu.popup()
            action()

    def repeat(self):
        self.player.repeat()
        self.player.wait_stop()

    def record(self):
        self.recorder.new()
        self.recorder.record()

    def make_menu(self):
        action_load = (u'Load', lambda: self.player.load(u'c:\\repeater\\eng.m4a'))
        action_exit = (u'Exit', self.exit)
        action_play = (u'Play', self.player.play)
        action_set_a = (u'Set A', self.player.set_ab)
        action_set_b = (u'Set B', self.player.set_ab)
        action_stop = (u'Stop', self.player.stop)
        action_pause = (u'Pause', self.player.pause)
        action_repeat = (u'Repeat', self.repeat)
        action_record = (u'Record', self.record)
        action_cancel_ab = (u'Cancel AB', self.player.cancel_ab)
        action_stop_record = (u'Stop Record', self.recorder.stop)
        action_compare = (u'Compare', self.compare)
        action_play_record = (u'Play Record', self.recorder.play)

        # Initial state
        if self.player.state() == Player.IDLE:
            menu = Menu('Idle', [action_load])
        # Audio file loaded
        elif self.player.state() == Player.READY:
            menu = Menu('Ready', [action_play])
        # Audio Playing
        elif self.player.state() == Player.PLAYING and self.player.point_a is None:
            menu = Menu('Playing', [action_stop, action_pause, action_set_a])
        elif self.player.state() == Player.PAUSED and self.player.point_a is None:
            menu = Menu('Paused', [action_play, action_stop])
        elif self.player.state() == Player.PLAYING and self.player.point_a is not None:
            menu = Menu('A set', [action_set_b, action_cancel_ab])
        elif (self.player.state() == Player.PAUSED and
                self.player.point_b is not None and
                self.recorder.state == AudioRecorder.NO_MEDIA):
            menu = Menu('AB set', [action_repeat, action_record, action_cancel_ab])
        elif self.recorder.state == AudioRecorder.RECORDING:
            menu = Menu('Recording', [action_stop_record])
        elif (self.player.state() == Player.PAUSED and
                self.player.point_b is not None and
                self.recorder.state == AudioRecorder.STOPPED):
            menu = Menu('Compare Ready', [action_compare, action_play_record, action_repeat, action_record, action_cancel_ab])
        else:
            menu = Menu()
        menu.append_item(action_exit)
        return menu

    def exit(self):
        self.exit_flag = True

if __name__ == '__main__':
    Repeater().run()
    print "Exited"
