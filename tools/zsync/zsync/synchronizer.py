__author__ = 'pma'

import pathlib
from datetime import datetime

from .meta_repo import MetaRepo
from .mvslib import *


class SyncError(Exception):
    pass

class Synchronizer():
    """Class to sync data sets"""

    def __init__(self, trans, root="."):
        self.trans = trans
        self.repo = MetaRepo(root)
        self.root = pathlib.Path(root)

    def pull(self, pdsn, local_path, patterns=None, force=False):
        dir = self.root / local_path
        rel_dir = dir.relative_to(self.root)
        if dir.is_file():
            raise NotADirectoryError
        if not dir.exists():
            dir.mkdir(parents=True)

        pulled = []
        failed = []
        ignored = []
        deleted = []

        pds = self.trans.list(pdsn)
        items = self.repo.get_dir(dir)

        if not patterns:
            item_path_set = {i.relpath for i in items}
            mem_paths = {rel_dir / memn : memn for memn in pds}  # move to MetaRepo
        else:
            item_path_set = {i.relpath for i in items if i.dsn.memn in patterns}
            mem_paths = {rel_dir / memn : memn for memn in pds if memn in patterns}  # move to MetaRepo

        # members in the meta info
        mem_path_set = set(mem_paths.keys())
        common = item_path_set & mem_path_set
        new_path = mem_path_set - common
        deleted_path = item_path_set - common

        for path, memn in mem_paths.items():
            member = pds[memn]
            if not (path in new_path or force):
                if ((self.repo.get(path).m_mtime == pds[memn].time) or
                            self.repo.get(path).f_mtime != datetime.fromtimestamp((self.root / path).stat().st_mtime)):
                    ignored.append(memn)
                    continue

            try:
                self.trans.get(pdsn, memn, self.root / path)
            except:
                failed.append(memn)
                raise
#                continue

            self.repo.add(path, pds, member)
            pulled.append(memn)

        for path in deleted_path:
            item = self.repo.get(path)
            memn = item.dsn.memn
            if not force:
                if item.f_mtime != datetime.fromtimestamp((self.root / path).stat().st_mtime):
                    ignored.append(memn)
                    continue

            deleted.append(memn)
            self.repo.delete(path)
            (self.root / path).unlink()

        return pulled, deleted, failed, ignored

    def get(self, pdsn, memn, local_path, force=False):
        p = pathlib.Path(local_path)
        if p.is_dir():
            raise IsADirectoryError
        if not p.parent.exists():
            p.parent.mkdir(parents=True)

        pds = self.trans.list(pdsn)
        member = pds[memn]
        self.trans.get(pdsn, memn, local_path)
        self.repo.add(p, pds, member)


