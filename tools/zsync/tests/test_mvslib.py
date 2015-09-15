__author__ = 'pma'

import  pytest
from zsync.mvslib import PDSInfo, MemberInfo, MemberNotFound

@pytest.fixture()
def mems():
    return [
        MemberInfo(name="TSTMEM1"),
        MemberInfo(name="TSTMEM2"),
        MemberInfo(name="TSTMEM3"),
    ]

@pytest.fixture()
def pds(mems):
    return PDSInfo("TST.PDS",
                   dsorg="PO",
                   recfm="FB",
                   lrecl=80,
                   volser="TST001",
                   members=mems)

def test_pds_new_instance_without_members():
    pds = PDSInfo("TST.PDS", dsorg="PO", recfm="FB", lrecl=80, volser="TST001")
    assert pds.dsn == "TST.PDS"
    assert pds.dsorg == "PO"
    assert pds.recfm == "FB"
    assert pds.lrecl == 80
    assert pds.volser == "TST001"
    assert pds.members == {}

def test_pds_new_instance_with_members(mems):
    pds = PDSInfo("TST.PDS", dsorg="PO", recfm="FB", lrecl=80, volser="TST001", members=mems)
    assert pds.dsn == "TST.PDS"
    assert pds.dsorg == "PO"
    assert pds.recfm == "FB"
    assert pds.lrecl == 80
    assert pds.volser == "TST001"
    assert pds.members == {m.name : m for m in mems}

def test_pds_get_member(pds):
    assert pds['TSTMEM1'].name == 'TSTMEM1'

def test_pds_get_non_existing_member(pds):
    with pytest.raises(MemberNotFound):
        print(pds['TSTMEM0'].name)

def test_pds_iterate_members(pds):
    assert sorted([m for m in pds]) == ['TSTMEM1', 'TSTMEM2', 'TSTMEM3']

def test_pds_if_has_member(pds):
    assert 'TSTMEM1' in pds
    assert 'TSTMEM0' not in pds

def test_pds_set_members(pds):
    assert 'TSTMEM4' not in pds
    pds['TSTMEM4'] = MemberInfo(name='TSTMEM4')
    assert pds['TSTMEM4'].name == 'TSTMEM4'

