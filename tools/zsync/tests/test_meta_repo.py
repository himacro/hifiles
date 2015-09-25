__author__ = 'pma'

from zsync.meta_repo import MetaRepo
from zsync.mvslib import PDSInfo
import pytest
import tempfile
from pathlib import Path
from utils import PDSRepo

pds_list =  (
    {
        "dsn" : "TST.PDS1",
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
)


@pytest.fixture()
def pds_repo():
    return PDSRepo(pds_list)

@pytest.fixture()
def work_dir(pds_repo):
    dir = tempfile.TemporaryDirectory()
    pds_repo.write_all(dir.name)

    return dir

@pytest.fixture()
def empty_repo(work_dir):
    return MetaRepo(work_dir.name)

@pytest.fixture()
def tstpds1(tstmem1):
    return PDSInfo("TSTPDS1", members=(tstmem1,))

@pytest.fixture()
def repo(work_dir, pds_repo):
    repo = MetaRepo(work_dir.name)

    pdsn = "TST.PDS1"
    pds = pds_repo[pdsn]
    for memn in pds:
        path = Path(pdsn, memn)
        repo.add(path, pds, pds[memn])

    return repo

def test_new_meta_repo():
    tmpd = tempfile.TemporaryDirectory()
    repo = MetaRepo(tmpd.name)
    assert repo.root == Path(tmpd.name).absolute()
    assert repo.len() == 0

def test_add(empty_repo, pds_repo):
    repo = empty_repo
    root = repo.root
    pds_repo.write_all(root)

    pdsn, memn = "TST.PDS1", "TSTMEM1"
    pds = pds_repo[pdsn]
    mem = pds[memn]
    path = Path(pdsn, memn)

    repo.add(path, pds, mem)

    assert repo.len() == 1

def test_delete(repo, pds_repo):
    pdsn, memn = "TST.PDS1", "TSTMEM1"
    path = Path(pdsn, memn)

    repo.delete(path)

    assert repo.len() == 2

def test_get(repo, pds_repo):
    pdsn, memn = "TST.PDS1", "TSTMEM1"
    pds = pds_repo[pdsn]
    mem = pds[memn]

    path = Path(pdsn, memn)

    item = repo.get(path)

    assert item.relpath == path
    assert item.m_mtime == mem.time

def test_get_dir(repo, pds_repo):
    pdsn = "TST.PDS1"
    items = repo.get_dir(Path(pdsn))

    assert len(items) == 3
