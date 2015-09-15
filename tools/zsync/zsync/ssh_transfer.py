__author__ = 'pma'

import paramiko
import socket


class SSHTransferError(Exception):
   pass

class SSHTransfer():
    """Transfer based on the SSH library paramiko"""

    def __init__(self, hostname=None, port=22, username=None, password=None):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password

        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                password=self.password
            )
        except paramiko.AuthenticationException as e:
            raise SSHTransferError("Authorization failed.")
        except (paramiko.SSHException, socket.error) as e:
            raise SSHTransferError("Connection Error: {}.".format(e))

        self.sftp = self.ssh.open_sftp()

    def list_hfs(self, path):
        return self.sftp.listdir(path)





