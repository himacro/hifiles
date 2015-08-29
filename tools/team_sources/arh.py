# -*- coding: utf-8 -*-

import sys
import os
import logging
from ftplib import FTP
from datetime import datetime
from datetime import date


class DataSetName():
    def __init__(self, dsname):
        self.qualifiers = dsname.split('.')
    
    def __str__(self):
        return self.plain()
    
    def plain(self):
        return '.'.join(self.qualifiers)
    
    def hlq(self, level=1):
        return '.'.join(self.qualifiers[:level])
    
    def llq(self, level=1):
        return '.'.join(self.qualifiers[-level:])
    
    def group(self):
        return '.'.join(self.qualifiers[1:-1])
    
    def project(self):
        return self.hlq()
    
    def type(self):
        return self.llq()
    
    def uss_form(self):
        return "//{}".format(self.plain())
    
    def ftp_abs_path(self):
        return self.quoted()

    def quoted(self):
        return "'{}'".format(self.plain())


class DataSetInfo():
    def __init__(self, dsorg="", recfm="", lrecl=0, blksize=0, referred="", 
                 volume="", dsn=None, ):
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
        string = ["{:<6} {:<5} {:<5} {:<5} {:<44}".format(
            "VOLUME", "DSORG", "RECFM", "LRECL", "DSNAME")]
        
        string.append("{:<6} {:<5} {:<5} {:<5} {:<44}".format(
            self.volume,
            self.dsorg,
            self.recfm,
            self.lrecl,
            self.dsn.plain))
        
        string.extend([str(m) for m in self.members])
            
        return "\n".join(string)
    
    def has_member(self, member_name):
        for m in self.members:
            if m.name == member_name:
                return True
        
        return False
    
    def is_pds(self):
        if self.dsorg in ["PO", "PO-E"]:
            return True
        else:
            return False
        
    def all_member_names(self):
        if self.is_pds():
            return [m.name for m in self.members]
            

class MemberInfo():
    def __init__(self, name="", changed=None, id=""):
        self.name = name
        self.changed = changed if changed else datetime(1900,1,1)
        self.id = id if id else "--------"
    
    def __str__(self):
       return "{:<8} {:<30} {:<8}".format(
           self.name, self.changed.strftime("%Y/%m/%d %H:%M:%S"), self.id)
        
    
class PylibFtp(FTP):
    def query_data_set(self, dsn, query_members=True):
        if not isinstance(dsn, DataSetName):
            dsn = DataSetName(dsn)
            
        result = []
        self.dir(dsn.quoted(), lambda line: result.append(line))
        volume, unit, referred, ext, used, recfm, lrecl, blksize, dsorg, _  \
            = result[1].expandtabs().split()
        dsinfo = DataSetInfo(
            dsorg, recfm, lrecl, blksize, referred, volume, dsn)
        
        if dsinfo.is_pds() and query_members:
            dsinfo.members = self.query_members(dsn)
            
        return dsinfo
   
    def query_members(self, dsn):
        if not isinstance(dsn, DataSetName):
            dsn = DataSetName(dsn)
        
        self.cwd(dsn.quoted())  
        output = []
        self.retrlines("LIST", lambda line: output.append(line) )

        logging.debug("Return from server:")
        for o in output:
            logging.debug(o)
        
        members = []
        for l in output[1:]:
            if not l:
                continue
            
            cols = l.expandtabs().split()
            if len(cols) == 1:
                m = MemberInfo(cols[0])
            else:
                name, _, _, changed_date, changed_time, _, _, _, id = cols
                changed = datetime.strptime(
                    " ".join([changed_date, changed_time]), "%Y/%m/%d %H:%M")
                m = MemberInfo(name, changed, id)
                
            members.append(m)

        return members
    
    def get_member(self, dsn, member, local_path=""):
        self.get_members(dsn, [member], local_path)
            
    def get_pds(self, dsn, local_path="", members=None):
        if not isinstance(dsn, DataSetName):
            dsn = DataSetName(dsn)

        if not os.path.isdir(local_path):
            logging.debug(local_path + " is not existing directory.")
            return False
            
        dsinfo = self.query_data_set(dsn)
        if not dsinfo.is_pds():
            # raise exception
            return False
        
        if not members:
            members = dsinfo.all_member_names()
        else:
            not_found = [m for m in members if not dsinfo.has_member(m)]
            if not_found:
                logging.debug("Members not found " + str(not_found))
                # raise exception
                return False
        
        logging.debug("CWDing to " + dsn.uss_form())
        self.cwd(dsn.uss_form())
        logging.debug("Done")
        for m in members:
            logging.debug("RETRieving: " + m)
            output = []
            self.retrlines("RETR " + m, 
                        lambda line: output.append(line + '\n'))
                

            path = os.path.join(local_path, m)
            if (True or not os.path.lexists(path)):
                logging.debug("Writing to " + os.path.abspath(path))
                with open(path, 'w') as f:
                    f.writelines(output)
                
            logging.debug("Done")
    
        return True
    

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', 
                        level=logging.DEBUG)
    remote = PylibFtp("dvlp", user="tspxm", passwd="Rocket2")
   # members = remote.query_members("TSPXM.JCL")
   # for m in members:
   #     print(m)
    
    remote.get_pds("TSPXM.JCL", "/home/pma/temp/JCL/", ["MXHAC058"])