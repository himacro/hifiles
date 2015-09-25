__author__ = 'pma'
import pytest
import tempfile
from pathlib import Path

from zsync.mvslib import *
from zsync.synchronizer import Synchronizer

from utils import PDSRepo, PseudoTransfer


pds_list =  (
    {
        "dsn" : "TST.PDS",
        "recfm": "FB",
        "lrecl": 80,
        "dsorg": "PO",
        "volser": "VOL001",
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
    },
    {
        "dsn" : "TST.PDS1",
        "recfm": "FB",
        "lrecl": 80,
        "dsorg": "PO",
        "volser": "VOL001",
        "members" : {
            "TSTMEM1" :{
                "time": "2014/09/10 09:44:09",
                "contents": "HELLO WORLD\nHELLO ZSYNC\nHELLO TST.PDS1\nHELLO TSTMEM1"
            },
            "TSTMEM2" :{
                "time": "2014/09/10 09:44:09",
                "contents": "HELLO WORLD\nHELLO ZSYNC\nHELLO TST.PDS1\nHELLO TSTMEM2"
            },
            "TSTMEM3" :{
                "time": "2014/09/10 09:44:09",
                "contents": "HELLO WORLD\nHELLO ZSYNC\nHELLO TST.PDS1\nHELLO TSTMEM3"
            }
        }
    }
)


@pytest.fixture()
def pds_repo():
    return PDSRepo(pds_list)

@pytest.fixture()
def trans(pds_repo):
    return PseudoTransfer(pds_repo)

@pytest.fixture()
def empty_dir():
    return tempfile.TemporaryDirectory()

@pytest.fixture()
def sync(trans, empty_dir):
    return Synchronizer(trans, empty_dir.name)

@pytest.fixture()
def do_sync(sync, pds_repo):
    for pdsn in pds_repo:
        sync.pull(pdsn)

def has_contents(local_path, content):
    with local_path.open('r') as f:
        return f.read() == content

def test_get(sync, pds_repo):
    pdsn = 'TST.PDS'
    memn = 'TSTMEM1'

    pds = pds_repo[pdsn]
    member = pds[memn]

    token = sync.get(pdsn, memn)

    assert token.pdsn == 'TST.PDS' and token.memn == "TSTMEM1"
    assert has_contents(token.path, pds_repo.read_member(pdsn, memn))
    assert token.path.stat().st_mtime == member.time.timestamp()

def test_get_from_non_existing_pds(sync):
    pdsn = 'TST.PDX'
    memn = 'TSTMEM1'

    with pytest.raises(DataSetNotFound):
        sync.get(pdsn, memn)

def test_get_a_non_existing_member(sync):
    pdsn = 'TST.PDS'
    memn = 'TSTMEM0'

    with pytest.raises(MemberNotFound):
        sync.get(pdsn, memn)

def test_pull_selected_members(sync, pds_repo):
    pdsn = 'TST.PDS'
    memns = ('TSTMEM1', 'TSTMEM2')

    pulled, _, _, _ = sync.pull(pdsn, memns)

    assert len(pulled) == len(memns)
    for token in pulled:
        assert token.memn in memns
        assert has_contents(token.path, pds_repo.read_member(pdsn, token.memn))

def test_pull_all_members(sync, pds_repo):
    pdsn = 'TST.PDS'
    pulled, _, _, _ = sync.pull(pdsn)
    assert len(pulled) == len(pds_repo[pdsn])

def test_pull_non_existing_member(sync, pds_repo):
    pdsn = 'TST.PDS'
    memns = ('TSTMEM0', 'TSTMEM1', 'TSTMEM2')

    pulled, _, _, _ = sync.pull(pdsn, memns)

    assert len(pulled) == 2
    assert 'TSTMEM0' not in [token.memn for token in pulled]


@pytest.mark.usefixtures("do_sync")
def test_pull_synced_member(sync):
    pdsn = 'TST.PDS'
    dir = sync.root / pdsn

    pulled, _, _, _ = sync.pull(pdsn)

    assert not pulled

@pytest.mark.usefixtures("do_sync")
def test_pull_modified_member(sync, pds_repo):
    pdsn = 'TST.PDS'
    memn = 'TSTMEM1'

    pds_repo[pdsn][memn].update_mtime("2014/09/11 11:00:03")

    pulled, _, _, _ = sync.pull(pdsn)

    assert len(pulled) == 1
    assert memn in (token.memn for token in pulled)

@pytest.mark.usefixtures("do_sync")
def test_pull_new_member(sync, pds_repo):
    pdsn = 'TST.PDS'
    memn = 'TSTMEM4'

    pds_repo.add_member(pdsn, memn)

    pulled, _, _, _ = sync.pull(pdsn)

    assert len(pulled) == 1
    assert memn in (token.memn for token in pulled)

@pytest.mark.usefixtures("do_sync")
def test_pull_deleting(sync, pds_repo):
    pdsn = 'TST.PDS'
    memn = 'TSTMEM1'

    del pds_repo[pdsn][memn]

    _, deleted, _, _ = sync.pull(pdsn)

    assert len(deleted) == 1
    assert memn in (token.memn for token in deleted)
