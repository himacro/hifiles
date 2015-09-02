import os
from fnmatch import fnmatch
import ftplib
from datetime import datetime


class DataSetInfo():

    def __init__(self, dsorg="", recfm="", lrecl=0, blksize=0, referred="",
                 volume="", dsn=""):
        self.dsn = dsn
        self.dsorg = dsorg
        self.recfm = recfm
        self.lrecl = lrecl
        self.blksize = blksize
        self.referred = datetime.strptime(referred, "%Y/%m/%d")
        self.volume = volume
        self.members = []

        return

    def __str__(self):
        return "VOL={:<6} DSORG={:<5} RECFM={:<5} LRECL={:<5} DSN={:<44}".format(
               self.volume, self.dsorg, self.recfm, self.lrecl, self.dsn)

    def is_pds(self):
        if "PO" in self.dsorg:
            return True
        else:
            return False


class PDSInfo():

    def __init__(self, dsinfo, members):
        self.dsinfo = dsinfo
        self.members = members


class MemberInfo():

    def __init__(self, name="", changed=None, id=""):
        self.name = name
        self.changed = changed if changed else datetime(1900, 1, 1)
        self.id = id if id else "--------"

    def __str__(self):
        return "{:<8} {:<30} {:<8}".format(
           self.name, self.changed.strftime("%Y/%m/%d %H:%M:%S"), self.id)


class MvsFTPException(Exception):
    pass


class MvsFTP():

    def __init__(self, host='', user='', passwd='', logger=print):
        if not logger:
            def do_nothing(msg):
                pass

            self.logger = do_nothing
        else:
            self.logger = logger

        self.ftp = ftplib.FTP()
        self.open(host, user, passwd)

    def open(self, host='', user='', passwd=''):
        self.logger("Connecting to {}".format(host))
        self.ftp.connect(host)
        self.logger("Logging with user {}".format(user))
        self.ftp.login(user, passwd)
        self.pwd()

    def pwd(self):
        resp = self.ftp.sendcmd('PWD')

        if "partitioned data set" in resp:
            dir_type = "PDS"
        elif "HFS" in resp:
            dir_type = "HFS"
        else:
            dir_type = "HLQ"

        return (resp[5: resp.index('" ')].replace("\'", "'"),
                dir_type)

    def cwd(self, path):
        resp = self.ftp.cwd("'" + path + "'")

        if "partitioned data set" in resp:
            dir_type = "PDS"
            remote_dir = \
                resp[resp.index('"'):resp.index(' is')].replace('"', "'")
        elif "HFS" in resp:
            dir_type = "HFS"
            remote_dir = \
                resp[resp.index('/'):resp.index(' is')]
        else:
            dir_type = "HLQ"
            remote_dir = \
                resp[resp.index('"'):resp.index(' is')].replace('"', "'")

        return [remote_dir, dir_type]

    def list_pds(self, pdsn):
        self.logger("Listing partitioned data set {}".format(pdsn))
        if self.cwd(pdsn)[1] != "PDS":
            raise MvsFTPException("Data set not a PDS.")

        lines = []
        try:
            self.ftp.dir(lambda line:  lines.append(line))
        except ftplib.error_perm:
            self.logger("Nothing listed")
            return []

        def parse_line(line):
            cols = line.expandtabs().split()
            if len(cols) == 1:
                return MemberInfo(cols[0])
            else:
                name, _, _, changed_date, changed_time, _, _, _, id = cols
                changed = datetime.strptime(
                    " ".join([changed_date, changed_time]), "%Y/%m/%d %H:%M")
                return MemberInfo(name, changed, id)

        return [parse_line(l) for l in lines[1:] if l]

    def list_by_hlq(self, hlq):
        self.logger("Listing data sets with HLQ {}".format(hlq))
        if not hlq:
            raise MvsFTPException("HLQ not specified.")

        if not hlq.endswith("."):
            hlq = hlq + '.'

        lines = []
        try:
            self.ftp.dir("'" + hlq + "**'", lambda line:  lines.append(line))
        except ftplib.error_perm:
            self.logger("Nothing listed")
            return []

        def parse_line(line):
            volume, unit, referred, ext, used, \
                recfm, lrecl, blksize, dsorg, dsn = line.expandtabs().split()

            return DataSetInfo(dsorg, recfm, lrecl, blksize,
                               referred, volume, dsn[1:-1])

        return [parse_line(l) for l in lines[1:] if l]

    def get_pds(self, pdsn, lpath, members=None, suffix=""):
        self.logger("Downloading partitoned data set {} to {}".format(pdsn, lpath))
        if self.cwd(pdsn)[1] != "PDS":
            raise MvsFTPException("Data set not a PDS.")

        if not members:
            members = self.list_pds(pdsn)

        self.logger("Members to download:")
        self.logger(' '.join([m.name for m in members]))

        if not os.path.exists(lpath):
            os.makedirs(lpath)

        for m in members:
            try:
                fn = os.path.join(lpath, m.name)
                if suffix:
                    fn = ".".join([fn, suffix])

                self.logger("Downloading {}({}) as {}".format(pdsn, m.name, fn))
                with open(fn, 'wt') as f:
                    os.utime(fn, (datetime(year=1900, month=1, day=1).timestamp(),) * 2)
                    self.ftp.retrlines("RETR " + m.name, lambda line: f.write(line + '\n'))
                os.utime(fn, (m.changed.timestamp(),) * 2)
            except ftplib.error_perm:
                self.logger("Failed to download {}({})".format(pdsn, m.name))

    def pull_pds(self, pdsn, lpath=".", patterns=None, suffix="", force=False):
        def is_candidate(m):
            if patterns:
                match = False
                for p in patterns:
                    if fnmatch(m.name, p):
                        match = True
                        break
                if not match:
                    return False

            if force:
                return True

            fn = os.path.join(lpath, m.name)
            if suffix:
                fn = ".".join([fn, suffix])

            if not os.path.exists(fn):
                return True

            if datetime.fromtimestamp(os.path.getmtime(fn)) < m.changed:
                return True

            return False

        self.logger("Checking partitoned data set {}".format(pdsn))
        members = [m for m in self.list_pds(pdsn) if is_candidate(m)]
        if members:
            self.get_pds(pdsn, lpath, members, suffix)
        else:
            self.logger("No member need to update for {}".format(pdsn))
