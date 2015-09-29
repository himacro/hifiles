__author__ = 'pma'

from pathlib import Path
from datetime import datetime
import os

from zsync.synchronizer import SyncError
from zsync.mvslib import *

class PseudoTransfer():
    def __init__(self, pds_repo):
        self.pds_repo = pds_repo

    def get(self, pdsn, memn, local_path):
        if pdsn not in self.pds_repo:
            raise DataSetNotFound

        if memn not in self.pds_repo[pdsn]:
            raise MemberNotFound

        self.pds_repo.write_member_to_file(pdsn, memn, local_path)

    def put(self, local_path, pdsn, memn):
        if pdsn not in self.pds_repo:
            raise DataSetNotFound

        self.pds_repo.write_file_to_member(pdsn, memn, local_path)

    def list(self, pdsn):
        if pdsn not in self.pds_repo:
            raise DataSetNotFound

        return self.pds_repo[pdsn]

    def delete(self, pdsn, memn):
        try:
            del self.pdss[pdsn][memn]
        except:
            pass

class PDSRepo:
    def __init__(self, pds_list):
        self.pdss = {}
        self.contents = {}
        for info in pds_list:
            pds = PDSInfo(dsn=info["dsn"],
                          recfm=info["recfm"],
                          lrecl=info["lrecl"],
                          dsorg=info["dsorg"],
                          volser=info["volser"])
            pdsn = info["dsn"]
            self.pdss[pdsn] = pds
            for memn, v in info["members"].items():
                self.update_member(pdsn, memn, v["contents"],v["time"])

    def update_member(self, pdsn, memn, content="", time=datetime.now()):
        pds = self.pdss[pdsn]
        pds[memn] = MemberInfo(name=memn, time=time)
        self.write_content(pdsn, memn, content)

    def read_content(self, pdsn, memn):
        return self.contents[self._keyify(pdsn, memn)]

    def write_content(self, pdsn, memn, content):
        self.contents[self._keyify(pdsn, memn)] = content

    @staticmethod
    def _keyify(*args):
        return ":".join(args)

    def write_member_to_file(self, pdsn, memn, path):
        file_path = Path(path)
        with file_path.open("w") as f:
            f.write(self.read_content(pdsn, memn))

    def write_file_to_member(self, pdsn, memn, path):
        file_path = Path(path)
        with file_path.open("r") as f:
            self.update_member(pdsn, memn, f.read())


    def write_pds_to_dir(self, pdsn, path):
        dir_path = Path(path)
        if path.exists() and not path.is_dir():
            raise NotADirectoryError

        if not path.exists():
            path.mkdir(parents=True)

        for m in self.pdss[pdsn]:
            self.write_member_to_file(pdsn, m, dir_path / m)

    def write_all(self, path):
        dir_path = Path(path)
        if dir_path.exists() and not dir_path.is_dir():
            raise NotADirectoryError

        for pdsn in self.pdss:
            self.write_pds_to_dir(pdsn, dir_path / pdsn)

    def __getitem__(self, k):
        return self.pdss[k]

    def items(self):
        return self.pdss.items()

    def __iter__(self):
        return iter(self.pdss)