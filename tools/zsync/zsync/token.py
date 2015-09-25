__author__ = 'pma'
from pathlib import Path
from .mvslib import PureDsn

class TokenPool:
    def __init__(self, root):
        self.root = Path(root).absolute()
        self.tokens = {}

    def _new_token(self, *args):
        #TODO: It should depend on the config file to get_token path from (pdsn, memn)
        path = Path(*args)
        return Token(self.root, path, *args)

    def get_token(self, *args):
        key = self._make_key(*args)
        if key in self.tokens:
            return self.tokens[key]
        else:
            token = self._new_token(*args)
            self.tokens[key] = token
            return token

    def _make_key(self, *args):
        return ":".join(args)


class Token:
    def __init__(self, root, path, *args):
        self.root = root
        self._dsn = PureDsn(*args)
        # TODO: handle exception that the path is not under the root
        self.rel_path = (self.root / path).absolute().relative_to(self.root)

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

    def match_memn(self, patterns):
        return self.memn in patterns
