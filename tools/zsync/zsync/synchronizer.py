__author__ = 'pma'

import pathlib
from datetime import datetime


class SyncError(Exception):
    pass


class Synchronizer():
    """Class to sync data sets"""
    def __init__(self, trans, comp=None):
        """
        :param trans: actual transfer backend
        :param comparator: to compare which file/member is newer
        :return: None
        """
        self.trans = trans
        if not comp:
            self.cmp = self.timestamp_cmp

    @staticmethod
    def timestamp_cmp(path, member):
        """
        :param path: local file path
        :param member: remote member info
        :return: True if file is newer, otherwise False
        """
        return datetime.fromtimestamp(path.stat().st_mtime) >= member.time

    def pull(self, pdsn, members=None, local_path='.', force=False):
        not_found = []
        ignored = []
        good = []
        bad = []

        p = pathlib.Path(local_path, pdsn)
        if p.exists() and not p.is_dir():
           raise SyncError("{} is existing but not a directory".format(p))

        if not p.exists():
            p.mkdir(parents=True)

        pds = self.trans.query_pds(pdsn)
        for m in members:
            if m in pds:
                m_path = p / m
                if (not force and m_path.is_file() and self.cmp(m_path, pds[m])):
                    ignored.append(m)
                else:
                    try:
                        self.trans.get(pds.dsn, m, str(m_path))
                        good.append(m)
                    except:
                        bad.append(m)
            else:
                not_found.append(m)

        return good, bad, ignored, not_found

    def get(self, pdsn, member, local_path, force=False):
        p = pathlib.Path(local_path)

        if p.is_dir():
            raise SyncError("{} is a existing directory but not a file!".format(p))

        if not p.parent.exists():
            p.parent.mkdir(parents=True)

        self.trans.get(pdsn, member, local_path)


