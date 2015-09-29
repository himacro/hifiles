__author__ = 'pma'

from zsync.meta import MetaRepo
from zsync.mvslib import PDSInfo
from zsync.token import TokenPool

import pytest
import tempfile
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
    token_pool = TokenPool(work_dir.name)
    return MetaRepo(work_dir.name, token_pool)

@pytest.fixture()
def tstpds1(tstmem1):
    return PDSInfo("TSTPDS1", members=(tstmem1,))

@pytest.fixture()
def repo(work_dir, pds_repo, empty_repo):
    repo = empty_repo

    pdsn = "TST.PDS1"
    pds = pds_repo[pdsn]
    for memn in pds:
        repo.add(pds, pds[memn])

    return repo

def test_new_meta_repo():
    tmpd = tempfile.TemporaryDirectory()
    token_pool = TokenPool(tmpd.name)
    repo = MetaRepo(tmpd.name, token_pool)

    assert repo.len() == 0

def test_add(empty_repo, pds_repo):
    repo = empty_repo
    root = repo.root
    pds_repo.write_all(root)

    pdsn, memn = "TST.PDS1", "TSTMEM1"
    pds = pds_repo[pdsn]
    mem = pds[memn]

    repo.add(pds, mem)

    assert repo.len() == 1

def test_delete(repo, pds_repo):
    pdsn, memn = "TST.PDS1", "TSTMEM1"

    repo.delete(pdsn, memn)

    assert repo.len() == 2

def test_get(repo, pds_repo):
    pdsn, memn = "TST.PDS1", "TSTMEM1"
    mem = pds_repo[pdsn][memn]

    item = repo.get(pdsn, memn)

    assert item.m_mtime == mem.time

def test_get_dir(repo, pds_repo):
    pdsn = "TST.PDS1"
    items = repo.get_by_pds(pdsn)

    assert len(items) == 3
