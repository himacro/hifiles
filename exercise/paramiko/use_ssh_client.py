import paramiko
import threading
import time


class SSHConnError(Exception):
    pass


class SSHConn():

    def __init__(self, setting):
        print('Initializating...')
        self.ssh = paramiko.SSHClient()

        print('Loading host keys....')
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print('Connecting....')
        self.ssh.connect('127.0.0.1', username='pma', password='asdf')

    def dir(self, path='.'):
        self.exec_and_output('ls -l ' + path)

    def exec_and_output(self, cmd):
        _, stdout, stderr = self.ssh.exec_command(cmd)
        output = [line[:-1] for line in stdout.readlines()]
        for ln in output:
            print(ln)
        return output


if __name__ == '__main__':
    conn = SSHConn()
    output = conn.dir()
    dirs = [ln.split(' ')[-1] for ln in output[1:]]
    for dir in dirs:
        threading.Thread(target=conn.dir,
                         args=(dir,)).start()

    time.sleep(5)
    print('main thread ended', flush=True)

