__author__ = 'pma'
import datetime


class MemberNotFound(Exception):
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


class MemberInfo():
    """ The class to represent information for PDS member """

    def __init__(self, name=None, time="1900/01/01 00:00:00", contents=None):
        self.name = name
        self.time = datetime.datetime.strptime(time, "%Y/%m/%d %H:%M:%S")
        self.contents = contents
