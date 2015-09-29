__author__ = 'pma'
from pathlib import Path
from .mvslib import PureDsn

class TokenPool:
    def __init__(self, root):
        self.root = Path(root).absolute()
        self.tokens = {}

    def _new_token(self, *args):
        # TODO: It should depend on the config file to get_by_dsn path from (pdsn, memn)
        rel_path = self._get_rel_path(Path(*args))
        return Token(self.root, rel_path, *args)

    def get_by_dsn(self, *args):
        key = self._make_key(*args)
        if key in self.tokens:
            return self.tokens[key]
        else:
            token = self._new_token(*args)
            self.tokens[key] = token
            return token

    def get_by_path(self, path):
        rel_path = self._get_rel_path(path)
        parts = rel_path.parts

        pdsn_key = self._make_key(parts[:-1])
        if pdsn_key in self.tokens:
            return self.get_by_dsn(self, *parts)
        else:
            return None

    def _get_rel_path(self, path):
        #TODO: handle exception that the path is not under the root
        return (self.root / path).absolute().relative_to(self.root)

    def _make_key(self, *args):
        return ":".join(args)


class Token:
    def __init__(self, root, rel_path, *args):
        self.root = root
        self.rel_path = rel_path
        self._dsn = PureDsn(*args)

    @property
    def path(self):
        return self.root / self.rel_path

    @property
    def as_key(self):
        return self._dsn.as_key

    def match_pdsn(self, pdsn):
        return self.pdsn == pdsn

    @property
    def dsn(self):
        return self._dsn.full

    @property
    def pdsn(self):
        return self._dsn.dsn

    @property
    def memn(self):
        return self._dsn.memn

    def match(self, patterns):
        return self.memn in patterns
