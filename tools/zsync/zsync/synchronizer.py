__author__ = 'pma'

import pathlib
from datetime import datetime

from .meta import MetaRepo
from .token import TokenPool
from .mvslib import *


class SyncError(Exception):
    pass

class Synchronizer():
    """Class to sync data sets"""

    def __init__(self, trans, root="."):
        self.root = pathlib.Path(root)
        self.trans = trans
        self.token_pool = TokenPool(self.root)
        self.repo = MetaRepo(self.root, self.token_pool)

    def status_remote(self, pdsn, memn=""):
        pass

    def pull(self, pdsn, patterns=None, force=False):
        dir_path = self.token_pool.get_token(pdsn).path
        if dir_path.is_file():
            raise NotADirectoryError
        if not dir_path.exists():
            dir_path.mkdir(parents=True)

        pds = self.trans.list(pdsn) # it's PdsInfo object
        items = self.repo.get_by_pds(pdsn) # it's a list of meta items

        tokens_at_remote = (self.token_pool.get_token(pdsn, memn) for memn in pds)
        tokens_in_repo = (item.token for item in items)

        if patterns:
            tokens_at_remote = {token for token in tokens_at_remote if token.match_memn(patterns)}
            tokens_in_repo = {token for token in tokens_in_repo if token.match_memn(patterns)}
        else:
            tokens_at_remote = set(tokens_at_remote)
            tokens_in_repo = set(tokens_in_repo)

        # members in the meta info
        tokens_in_common = tokens_at_remote & tokens_in_repo
        tokens_new_at_remote = tokens_at_remote - tokens_in_common
        tokens_deleted_at_remote = tokens_in_repo - tokens_in_common

        def _only_updated_at_remote(token):
            pdsn, memn, path = token.pdsn, token.memn, token.path
            item = self.repo.get(pdsn, memn)
            return ((item.m_mtime < pds[memn].time) and
                    (item.f_mtime == datetime.fromtimestamp(path.stat().st_mtime)))


        tokens_to_get = {token for token in tokens_at_remote
                         if (force or
                             (token in tokens_new_at_remote) or
                             _only_updated_at_remote(token))}
        pulled = set()
        failed = set()
        for token in tokens_to_get:
            memn, path = token.memn, token.path
            try:
                self.trans.get(pdsn, memn, path)
            except:
                failed.add(token)
                continue

            self.repo.add(pds, pds[memn])
            pulled.add(token)

        def _not_updated_at_local(token):
            pdsn, memn, path = token.pdsn, token.memn, token.path
            item = self.repo.get(pdsn, memn)
            return  item.f_mtime == datetime.fromtimestamp(path.stat().st_mtime)

        tokens_to_delete = {token for token in tokens_deleted_at_remote
                            if (force or _not_updated_at_local(token))}
        for token in tokens_to_delete:
            memn, path = token.memn, token.path
            path.unlink()
            self.repo.delete(pdsn, memn)

        deleted = tokens_to_delete
        ignored = tokens_at_remote - (pulled | deleted | failed)

        return pulled, deleted, failed, ignored

    def get(self, pdsn, memn, force=False):
        token = self.token_pool.get_token(pdsn, memn)
        memn, path = token.memn, token.path
        if path.is_dir():
            raise IsADirectoryError
        if not path.parent.exists():
            path.parent.mkdir(parents=True)

        pds = self.trans.list(pdsn)
        member = pds[memn]
        self.trans.get(pdsn, memn, path)
        self.repo.add(pds, member)

        return token
