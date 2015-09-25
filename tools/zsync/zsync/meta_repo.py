__author__ = 'pma'
from pathlib import Path
from datetime import datetime
from .mvslib import PureDsn

class MetaItem:
    def __init__(self, relpath, f_mtime, pdsn, memn, m_mtime):
        self.relpath = relpath
        self.f_mtime = f_mtime
        self.dsn = PureDsn(pdsn, memn)
        self.m_mtime = m_mtime

    def key(self):
        return str(self.relpath)

    def match(self, dir_path):
        return self.relpath.parent == dir_path

class MetaRepo():
    def __init__(self, root):
        self.root = Path(root).absolute()
        self.dir = self.root / ".meta"
        if not self.dir.exists():
            self.dir.mkdir()
        self.items = {}

    def _relpath(self, path):
        return self._abspath(path).relative_to(self.root)

    def _abspath(self, path):
        return Path(self.root, path)

    def _keyify(self, path, pdsn="", memn=""):
        return str(self._relpath(path))

    def add(self, path, pds, mem):
        p = self._abspath(path)
        f_mtime = datetime.fromtimestamp(p.stat().st_mtime)
        item = MetaItem(self._relpath(p), f_mtime, pds.dsn, mem.name, mem.time)

        self.items[self._keyify(path)] = item

    def update(self, path, pds, mem):
        self.add(path, pds, mem) # update = add ???

    def get(self, path):
        return self.items.get(self._keyify(path), None)

    def delete(self, path):
        del self.items[self._keyify(path)]

    def get_dir(self, dir):
        dir_path = self._relpath(dir)
        return {v for v in self.items.values() if v.match(dir_path)}

    def len(self):
        return len(self.items)

    def __len__(self):
        return self.len()
