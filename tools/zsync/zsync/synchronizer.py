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

    def _member_tokens(self, pds, patterns=None):
        pdsn = pds.dsn
        items = self.repo.get_by_pds(pdsn)

        m_tokens = {self.token_pool.get_by_dsn(pdsn, memn) for memn in pds}
        i_tokens = {item.token for item in items}

        if patterns:
            m_tokens = {token for token in m_tokens if token.match(patterns)}
            i_tokens = {token for token in i_tokens if token.match(patterns)}

        common = m_tokens & i_tokens
        new = m_tokens - common
        deleted = i_tokens - common

        def _is_member_changed(token):
            memn = token.memn
            if self.repo.get(pdsn, memn).m_mtime != pds[memn].time:
                return True
            else:
                return False

        changed = set(filter(_is_member_changed, common))
        unchanged = common - changed

        return {"new" : new,
                "deleted" : deleted,
                "changed" : changed,
                "unchanged" : unchanged}


    def _file_tokens(self, pds_token, patterns=None):
        pdsn = pds_token.pdsn
        items = self.repo.get_by_pds(pds_token.pdsn)

        file_tokens = {self.token_pool.get_by_dsn(pdsn, f_path.stem)
                        for f_path in pds_token.path.iterdir() if f_path.is_file()}
        item_tokens = {item.token for item in items}

        if patterns:
            file_tokens = {token for token in file_tokens if token.match(patterns)}
            item_tokens = {token for token in item_tokens if token.match(patterns)}

        common = file_tokens & item_tokens
        new = file_tokens - common
        deleted = item_tokens - common

        def _is_file_changed(token):
            if self.repo.get(pdsn, token.memn).f_mtime != datetime.fromtimestamp(token.path.stat().st_mtime):
                return True
            else:
                return False

        changed = set(filter(_is_file_changed, common))
        unchanged = common - changed

        return {"new" : new,
                "deleted" : deleted,
                "changed" : changed,
                "unchanged" : unchanged}

    def pull(self, pdsn, patterns=None, force=False):
        pds_token = self.token_pool.get_by_dsn(pdsn)
        dir_path = pds_token.path
        if dir_path.is_file():
            raise NotADirectoryError
        if not dir_path.exists():
            dir_path.mkdir(parents=True)

        pds = self.trans.list(pdsn)

        m_tokens = self._member_tokens(pds, patterns)
        f_tokens = self._file_tokens(pds_token, patterns)

        to_get = m_tokens["new"] | (m_tokens["changed"] & f_tokens["unchanged"])
        to_delete = m_tokens["deleted"] & f_tokens["unchanged"]

        pulled = set()
        failed = set()
        for token in to_get:
            memn, path = token.memn, token.path
            try:
                self.trans.get(pdsn, memn, path)
            except:
                failed.add(token)
                continue

            self.repo.add(pds, pds[memn])
            pulled.add(token)

        for token in to_delete:
            memn, path = token.memn, token.path
            path.unlink()
            self.repo.delete(pdsn, memn)

        deleted = to_delete
        ignored = (m_tokens["new"] | m_tokens["deleted"] | m_tokens["changed"]) - (pulled | deleted | failed)

        return pulled, deleted, failed, ignored

    def get(self, pdsn, memn, force=False):
        token = self.token_pool.get_by_dsn(pdsn, memn)
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

    def push(self, pdsn, patterns=None, force=False):
        pds_token = self.token_pool.get_by_dsn(pdsn)
        dir_path = pds_token.path
        if not dir_path.is_dir():
            raise NotADirectoryError

        pds = self.trans.list(pdsn)
        m_tokens = self._member_tokens(pds, patterns)
        f_tokens = self._file_tokens(pds_token, patterns)

        to_put = f_tokens["new"] | (f_tokens["changed"] & m_tokens["unchanged"])
        to_delete = f_tokens["deleted"] & m_tokens["unchanged"]

        pushed = set()
        failed = set()
        for token in to_put:
            memn, path = token.memn, token.path
            try:
                self.trans.put(path, pdsn, memn)
            except:
                failed.add(token)
                continue

            self.repo.add(pds, pds[memn])
            pushed.add(token)

        for token in to_delete:
            memn = token.memn
            self.trans.delete(pdsn, memn)

        deleted = to_delete
        ignored = (f_tokens["new"] | f_tokens["deleted"] | f_tokens["changed"]) - (pushed | deleted | failed)

        return pushed, deleted, failed, ignored
