__author__ = 'pma'
import pytest
import tempfile
from pathlib import Path
from datetime import datetime
import os

from zsync.synchronizer import Synchronizer, SyncError
from zsync.mvslib import PDSInfo, MemberInfo, MemberNotFound

class PseudoTransfer():
    def __init__(self, pds):
        self.data_sets = {}
        self.pds = pds

    def get(self, pdsn, member, local_path):
        try:
            with open(local_path, 'w') as f:
                f.write(self.pds[pdsn][member].contents)
            mtime = self.pds[pdsn][member].time.timestamp()
            os.utime(str(local_path), times=(mtime,) * 2)

        except KeyError as e:
            if pdsn in str(e):
                raise SyncError("Data set '{}' not found".format(pdsn))
        except MemberNotFound:
                raise SyncError("Member {} not found".format(member))

    def query_pds(self, pdsn):
        return self.pds[pdsn]

def pds_from_dict(dic):
    dsinfo = dic["info"]
    pds = PDSInfo(dsn=dsinfo["dsn"],
                  recfm=dsinfo["recfm"],
                  lrecl=dsinfo["lrecl"],
                  dsorg=dsinfo["dsorg"],
                  volser=dsinfo["volser"])

    for k, v in dic["members"].items():
        pds[k] = MemberInfo(name=k, time=v["time"], contents=v["contents"])

    return pds


@pytest.fixture()
def tst_pds():
    pds_dict =  {
        "info": {
            "dsn" : "TST.PDS",
            "recfm": "FB",
            "lrecl": 80,
            "dsorg": "PO",
            "volser": "VOL001"
        },
        "members" : {
            "TSTMEM1" :{
                "time": "2014/09/10 09:44:09",
                "contents": "HELLO WORLD\nHELLO ZSYNC\nHELLO TST.PDS\nHELLO TSTMEM1"
            },
            "TSTMEM2" :{
                "time": "2014/09/10 09:44:09",
                "contents": "HELLO WORLD\nHELLO ZSYNC\nHELLO TST.PDS\nHELLO TSTMEM2"
            },
            "TSTMEM3" :{
                "time": "2014/09/10 09:44:09",
                "contents": "HELLO WORLD\nHELLO ZSYNC\nHELLO TST.PDS\nHELLO TSTMEM3"
            }
        }
    }
    return {pds_dict["info"]["dsn"] : pds_from_dict(pds_dict)}


@pytest.fixture()
def trans(tst_pds):
    return PseudoTransfer(tst_pds)

@pytest.fixture()
def sync(pseudo_trans):
    return Synchronizer(pseudo_trans)

@pytest.fixture()
def empty_local_dir():
    return tempfile.TemporaryDirectory()

@pytest.fixture()
def local_dir_with_new_tstmem1(empty_local_dir, tst_pds):
    pdsn = "TST.PDS"
    member = "TSTMEM1"
    path = Path(empty_local_dir.name, pdsn, member)
    path.parent.mkdir(parents=True)
    with path.open("w") as f:
        f.write(tst_pds[pdsn][member].contents)
    time = tst_pds[pdsn][member].time.timestamp()
    os.utime(str(path), (time,) * 2)

    return empty_local_dir


def has_contents(local_path, contents):
    with local_path.open('r') as f:
        return f.read() == contents

def test_get(sync, tst_pds, empty_local_dir):
    pdsn = 'TST.PDS'
    member = 'TSTMEM1'
    path = Path(empty_local_dir.name, pdsn, member)

    sync.get(pdsn, member, str(path))
    assert has_contents(path,
                        tst_pds[pdsn][member].contents)

def test_get_from_non_existing_pds(sync, tst_pds, empty_local_dir):
    pdsn = 'TST.PSX'
    member = 'TSTMEM1'
    path = Path(empty_local_dir.name, pdsn, member)

    with pytest.raises(SyncError) as excinfo:
        sync.get(pdsn, member, str(path))
    assert "Data set" in str(excinfo.value)

def test_get_a_non_existing_member(sync, tst_pds, empty_local_dir):
    pdsn = 'TST.PDS'
    member = 'TSTMEM0'
    path = Path(empty_local_dir.name, pdsn, member)

    with pytest.raises(SyncError) as excinfo:
        sync.get(pdsn, member, str(path))
    assert "Member" in str(excinfo.value)

def test_force_pull_to_empty_local(sync, tst_pds, empty_local_dir):
    pdsn = 'TST.PDS'
    members = ['TSTMEM1', 'TSTMEM2']
    path = Path(empty_local_dir.name)

    sync.pull(pdsn, members, str(path), force=True)

    for m in members:
        assert has_contents(path / pdsn / m, tst_pds[pdsn][m].contents)

def test_force_pull_non_existing_member(sync, tst_pds, empty_local_dir):
    pdsn = 'TST.PDS'
    members = ['TSTMEM0', 'TSTMEM1', 'TSTMEM2']
    path = Path(empty_local_dir.name)

    good, _, _, not_found = sync.pull(pdsn, members, str(path), force=True)

    assert good == ['TSTMEM1', 'TSTMEM2']
    assert not_found == ['TSTMEM0']
    for m in good:
        m_path = path / pdsn / m
        member = tst_pds[pdsn][m]
        assert has_contents(m_path, member.contents)
        assert datetime.fromtimestamp(m_path.stat().st_mtime) == member.time

def test_pull_older_member(sync, tst_pds, local_dir_with_new_tstmem1):
    pdsn = 'TST.PDS'
    members = ['TSTMEM1', 'TSTMEM2']
    path = Path(local_dir_with_new_tstmem1.name)

    good, _, ignored, _ = sync.pull(pdsn, members, str(path))

    assert good == ['TSTMEM2']
    assert ignored == ['TSTMEM1']
    for m in good:
        assert has_contents(path / pdsn / m, tst_pds[pdsn][m].contents)


