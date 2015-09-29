__author__ = 'pma'
from pathlib import Path
from datetime import datetime
#from .token import Token
#from .mvslib import PureDsn


class MetaItem:
    def __init__(self, token, f_mtime, m_mtime):
        self.token = token
        self.f_mtime = f_mtime
        self.m_mtime = m_mtime

    def match_pds(self, pdsn):
        return (self.token.pdsn == pdsn and self.token.memn)

class MetaRepo():
    def __init__(self, root, token_pool):
        self.root = Path(root).absolute()
        self.dir = self.root / ".meta"
        if not self.dir.exists():
            self.dir.mkdir()
        self.items = {}
        self.token_pool = token_pool

    def add(self, pds, mem):
        token = self.token_pool.get_by_dsn(pds.dsn, mem.name)

        path, pdsn, memn = token.path, token.pdsn, token.memn
        f_mtime = datetime.fromtimestamp(path.stat().st_mtime)

        self.items[token.as_key] = MetaItem(token, f_mtime, mem.time)

    def update(self, pds, mem):
        self.add(pds, mem) # update = new_token ???

    def get(self, pdsn, memn):
        token = self.token_pool.get_by_dsn(pdsn, memn)
        return self.items[token.as_key]

    def delete(self, pdsn, memn):
        token = self.token_pool.get_by_dsn(pdsn, memn)
        del self.items[token.as_key]

    def get_by_pds(self, pdsn):
        return {item for item in self.items.values() if item.match_pds(pdsn)}

    def len(self):
        return len(self.items)

    def __len__(self):
        return self.len()
