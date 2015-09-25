__author__ = 'pma'
__all__ = ["PDSInfo", "MemberInfo", "MemberNotFound", "DataSetNotFound", "PureDsn"]
from datetime import datetime

class MemberNotFound(Exception):
    pass

class DataSetNotFound(Exception):
    pass

class PDSInfo():
    """ The class to represent information for PDS """

    def __init__(self,
                 dsn=None,
                 dsorg="PO",
                 recfm=None,
                 lrecl=None,
                 volser=None,
                 members=None):
        self.dsn = dsn
        self.dsorg = dsorg
        self.recfm = recfm
        self.lrecl = lrecl
        self.volser = volser

        self.members = {m.name : m for m in members} if members else {}

    def __getitem__(self, k):
        try:
            return self.members[k]
        except KeyError:
            raise MemberNotFound("Member {} not found".format(k))

    def __iter__(self):
        return iter(self.members)

    def __setitem__(self, k, v):
        self.members[k] = v

    def __delitem__(self, k):
        del self.members[k]

    def items(self):
        return self.members.items()

    def member_names(self):
        return self.members.keys()

    def len(self):
        return len(self.members)

    def __len__(self):
        return self.len()

class MemberInfo():
    """ The class to represent information for PDS member """

    def __init__(self, name, time=None, contents=None):
        self.name = name
        self.contents = contents
        self.update_mtime(time)

    def update_mtime(self, time):
        if time:
            if isinstance(time, datetime):
                self.time = time
            else:
                self.time = datetime.strptime(time, "%Y/%m/%d %H:%M:%S")
        else:
            self.time = datetime.now()

class PureDsn():
    def __init__(self, *args):
        len_ = len(args)
        self.dsn = args[0] if len_ > 0 else ""
        self.memn = args[1] if len_ > 1 else ""

    def _join(self, sep=":"):
        return sep.join((self.dsn, self.memn))

    @property
    def full(self):
        if self.memn:
            return "{}.({})".format(self.dsn, self.memn)
        if self.memn:
            return self.dsn

    @property
    def as_key(self):
        return self._join()

    def __eq__(self, other):
        return (self.dsn, self.memn) == (other._dsn, other.memn)

    def __hash__(self):
        return hash(self._join())


