import pytest
import os
import sys

zsync_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "../")
sys.path.insert(0, zsync_path)
from zsync import ssh_transfer

@pytest.fixture(scope="module")
def ssh_trans():
    return ssh_transfer.SSHTransfer(
        hostname="rs31",
        username="tspxm",
        password="Rocket2")

def test_list_uss_directory(ssh_trans):
    assert "tspxm" in ssh_trans.list_hfs("/u")





















