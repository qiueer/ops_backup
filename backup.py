#!/usr/bin/env python
# -*- encoding=utf-8 -*-
###
###

import sys
import os
import re
import traceback
import tarfile
from optparse import OptionParser

from lib.base.slog import slog
from lib.base.sdate import sdate
from lib.base.cmds import cmds
from lib.helper.parse import BUp


reload(sys)
sys.setdefaultencoding('utf8')

def get_realpath():
    return os.path.split(os.path.realpath(__file__))[0]

def get_binname():
    return os.path.split(os.path.realpath(__file__))[1]

try:
    from shutil import which  # Python >= 3.3
except ImportError:
    import os, sys
    def which(cmd, mode=os.F_OK | os.X_OK, path=None):
        def _access_check(fn, mode):
            return (os.path.exists(fn) and os.access(fn, mode)
                    and not os.path.isdir(fn))

        if os.path.dirname(cmd):
            if _access_check(cmd, mode):
                return cmd
            return None
    
        if path is None:
            path = os.environ.get("PATH", os.defpath)
        if not path:
            return None
        path = path.split(os.pathsep)
    
        if sys.platform == "win32":
            if not os.curdir in path:
                path.insert(0, os.curdir)
    
            pathext = os.environ.get("PATHEXT", "").split(os.pathsep)
            if any(cmd.lower().endswith(ext.lower()) for ext in pathext):
                files = [cmd]
            else:
                files = [cmd + ext for ext in pathext]
        else:
            files = [cmd]
    
        seen = set()
        for dir in path:
            normdir = os.path.normcase(dir)
            if not normdir in seen:
                seen.add(normdir)
                for thefile in files:
                    name = os.path.join(dir, thefile)
                    if _access_check(name, mode):
                        return name
        return None
    
def get_right_content(content):
    try:
        content = content.decode("utf8")
    except Exception:
        try:
            content = content.decode("gbk")
        except Exception:
            try:
                content = content.decode("GB2312")
            except Exception:
                pass
    return content

class Backup(object):
    def __init__(self, conffile, logfile, debug=False):
        self._conffile = conffile
        key_map = {"func": u"功能说明", "srcfiles": u"备份目录(文件)", "destdir": u"存储目录", "excludes": u"排除目录(文件)", "zip":u"是否压缩", "keep": "保留份数"}
        key_order = ["func", "srcfiles", "destdir", "excludes", "zip", "keep"]
        self._conf_instance = BUp(conffile, key_map=key_map, key_check=None, key_order=key_order, max_key_len=20)
        self._logger = slog(logfile, debug=debug)
        
    def get_conf_parse_ins(self):
        return self._conf_instance
    
    def get_backup_conf(self,sid):
        try:
            conf = self._conf_instance.get_section_dict(sid)
            if not conf:
                self._logger.warn("not sid:{0} found.".format(sid))
                return dict()
            return conf
        except:
            return dict()
        
    def check(self, sid):
        try:
            conf = self.get_backup_conf(sid)
            if not conf: return False
            srcfiles = conf.get("srcfiles", "")
            destdir = conf.get("destdir", "")
            excludes = conf.get("excludes", "")
            zip = conf.get("zip", "")
            keep = conf.get("keep", "")
            return True
        except:
            return False
        
    def adjust_win_path(self, path):
        while '\\\\' in path:path=path.replace('\\\\', '\\')
        return u"{0}".format(path)
    
    def adjust_unix_path(self, path):
        while '//' in path:path=path.replace('//', '/')
        return u"{0}".format(path)
    
    def path_trans(self, path):
        '''
        windows path to cygwin path
        '''
        path = path.replace(":", '')
        path = u"{0}{1}".format('/cygdrive/', path)
        path = self.adjust_win_path(path)
        path = self.adjust_unix_path(path)
        while '\\' in path:path=path.replace('\\', '/')
        return u"{0}".format(path)

    def tar_gz(self, directory, fname=None):
        try:
            cur_path = os.getcwd()
            pos = directory.rfind(os.path.sep)
            predir = directory[0:pos]
            destfile = directory[pos+1:]
            if not fname: fname = destfile+".tar.gz"
            
            os.chdir(predir)
            tar = tarfile.open(fname, 'w:gz')
            
            ## a file
            if os.path.isfile(directory):
                tar.add(destfile)
                tar.close()
                os.chdir(cur_path)
                return True
            
            ## directory
            for root, dirs, files in os.walk(destfile):
                for f in files:
                    fullpath = os.path.join(root, f)
                    tar.add(fullpath)
            tar.close()
            os.chdir(cur_path)
            return True
        except:
            tb = traceback.format_exc()
            self._logger.warn(tb)
            return False
    
    def delete(self, directory):
        try:
            if "win32" in sys.platform:
                #if directory.strip() in ['', 'c:\\', 'C:\\', 'd:\\', 'D:\\', 'e:\\', 'E:\\', 'f:\\', 'F:\\', 'g:\\', 'G:\\']: return False
                if len(directory.strip()) <=3 :return False
                if os.path.isfile(directory):
                    cmdstr = u"del /s /q {0}".format(directory)
                else:
                    cmdstr = u"rd /s /q {0}".format(directory)
                os.system(cmdstr.encode("gbk"))
            
            if "linux" in sys.platform:
                if directory.strip() in ['', '/', '/usr/bin', '/sbin', '/etc']: return False
                cmdstr = u"rm -fr {0}".format(directory)
                os.system(cmdstr)
            return True
        except:
            tb = traceback.format_exc()
            self._logger.warn(tb)
            return False
        
    def sort_file(self, directory):
        def compare(x, y):
            '''
            降序
            '''
            stat_x = os.stat(directory + "/" + x)  
            stat_y = os.stat(directory + "/" + y)  
            if stat_x.st_ctime > stat_y.st_ctime:  
                return -1  
            elif stat_x.st_ctime < stat_y.st_ctime:  
                return 1  
            else:  
                return 0
        if os.path.exists(directory) == False: return None
        iterms = os.listdir(directory)  
        iterms.sort(compare)
        return iterms

    def oh(self, dirfile, destdir, excludes):
        try:
            if os.path.exists(destdir) == False:
                os.mkdir(destdir)
            dirfile = dirfile.strip("\\")

            excl_file = os.path.join(destdir, ".TMP_EXCLUDE.txt")
            ex_ln = re.split("[,|;]", excludes)
            fd = open(excl_file, "a")
            fd.write("\n".join(ex_ln))
            fd.close()
            
            cmdstr = ""
#             if sys.platform == "win32":
#                 excl_str = "/exclude:{0}".format(excl_file)
#                 xcopy = which("xcopy")
#                 if not xcopy:
#                     binname = "bin" + os.path.sep + "rsync.exe"
#                     rsync = os.path.join(get_realpath(), binname)
            if sys.platform == "win32": # window
                rsync = which("rsync")
                if not rsync:
                    binname = "bin" + os.path.sep + "rsync.exe"
                    rsync = os.path.join(get_realpath(), binname)
                
                dirfile_trans = self.path_trans(dirfile)
                destdir_trans = self.path_trans(destdir)
                excl_file_trans = self.path_trans(excl_file)
                dirfile_trans = dirfile_trans.encode(encoding='UTF-8')
                destdir_trans = destdir_trans.encode(encoding='UTF-8')
                excl_file_trans = excl_file_trans.encode(encoding='UTF-8')
                excl_str = u"--exclude-from='{0}'".format(excl_file_trans)
                cmdstr = u"{0} -arpv {1} '{2}' '{3}'".format(rsync, excl_str, dirfile_trans, destdir_trans)
            elif 'linux' in sys.platform: ## linux rsync
                excl_str = u"--exclude-from='{0}'".format(excl_file)
                rsync = which("rsync")
                if rsync:
                    cmdstr = u"{0} -arpv {1} '{2}' '{3}'".format(rsync, excl_str, dirfile, destdir)
                    
            if not cmdstr:
                self._logger.warn(u"can not find rsync command".format())
                return cmdstr
            
            cmdstr = u"{0}".format(cmdstr)
            return cmdstr

        except:
            tb =  traceback.format_exc()
            self._logger.error(tb)
            return None

    def run(self, sid):
        try:
            conf = self.get_backup_conf(sid)
            if not conf: return False
            srcfiles = conf.get("srcfiles", "")
            destdir = conf.get("destdir", "")
            excludes = conf.get("excludes", "")
            zip_flag = conf.get("zip", "")
            keep = conf.get("keep", "")
            timeout = int(conf.get("timeout", 0))
            
            srcfiles = srcfiles.strip()
            destdir = destdir.strip()
            
            if srcfiles == "" or destdir == "": 
                msg = u"srcfiles:{0} or destdir:{1} is empty.".format(srcfiles, destdir)
                print msg
                self._logger.warn(msg)
                return False
            
            file_ln = re.split("[,|;|\s]+", srcfiles)
            if not file_ln: 
                return False
            
            auto_destdir = os.path.join(destdir, sdate().datetime_ex())
            
            if not os.path.exists(destdir):
                os.makedirs(destdir)
                os.makedirs(auto_destdir)

            for (idx,f) in enumerate(file_ln):
                f = unicode(f.strip(), "utf-8")
                if not f:continue
                if not os.path.exists(f):
                    msg = u"File Not Exist. File: {0}".format(f)
                    print msg
                    self._logger.warn(msg)
                    continue

                cmdstr = self.oh(f, auto_destdir, excludes)
                print u"[FILE-{0}]".format(idx+1)
                print u"  FROM: {0}".format(f)
                print u"    TO: {0}".format(auto_destdir)
                print u"  KEEP: {0}".format(keep)
                print u"   ZIP: {0}".format(zip_flag)
                #print u"CMDSTR: {0}".format(cmdstr)
                if sys.platform == 'win32': ## 解决中文路径引起的错误
                    cmdstr = cmdstr.encode("gbk")
                
                command = cmds(cmdstr, timeout=timeout)
                (stdo, stde, retcode) = (command.stdo(), command.stde(), command.code())
                
                logdict = {
                    "cmdstr": get_right_content(cmdstr),
                    "stdo": stdo,
                    "stde": stde,
                    "retcode": retcode,
                }
                self._logger.dictlog(level="info", **logdict)

                if retcode == 0:
                    print(u"=> backup result: SUCCESS" )
                    if zip_flag.strip() == "1":
                        directory = os.path.join(auto_destdir, f.split(os.path.sep)[-1])
                        tarflag = self.tar_gz(directory)
                        if tarflag == True:
                            print(u"=> tar result: SUCCESS" )
                            self.delete(directory)
                        else:
                            print(u"=> tar result: SUCCESS" )
                else:
                    print(u"=> backup result: FAILURE")
                    
            ## sort dir desc by ctime
            dirs = self.sort_file(destdir)
            keep = int(str(keep).strip())
            if keep <= 0: return
            ## delete old version
            del_dirs = dirs[keep-1:]
            for d in del_dirs:
                del_path = os.path.join(destdir,d)
                self.delete(del_path)
                print u"=> Delete: {0}".format(del_path)

        except:
            tb = traceback.format_exc()
            self._logger.error(tb)
        
def main():
    try:
        parser = OptionParser()
        parser.add_option("-i", "--id",  
                  action="store", dest="id", default=None,  
                  help="which id to backup", metavar="ID")
        parser.add_option("-c", "--conf",  
                  action="store", dest="conf", default=None,  
                  help="configure file", metavar="CONFFILE")
        parser.add_option("-l", "--list", dest="list", default=False,
                  action="store_true", help="list all the configure")
        parser.add_option("-d", "--debug", dest="debug", default=False,
                  action="store_true", help="if open debug module")

        (options, args) = parser.parse_args()
        sid = options.id
        conffile = options.conf
        list_flag = options.list
        debug = options.debug
        
        if not conffile:
            conffile = get_realpath() + "/etc/backup.conf"

        if os.path.exists(conffile) == False:
            conffile = "/etc/backup.conf"
            if os.path.exists(conffile) == False:
                parser.print_help()
                sys.exit(1)

        logdir = get_realpath() + os.path.sep + "log" + os.path.sep
        logfile = logdir + "ops_backup.log"
        if not os.path.exists(logdir): os.mkdir(logdir) 
        bk = Backup(conffile, logfile, debug=debug)
        ## list all
        if list_flag == True and not sid:
            bk.get_conf_parse_ins().list()
            return
        
        if list_flag == True and sid:
            bk.get_conf_parse_ins().list_one(sid)
            return
        
        if sid:
            bk.run(sid)
            return 
        
        parser.print_help()
        
    except Exception, expt:
        tb = traceback.format_exc()
        print tb
        parser.print_help()
     
if __name__ == "__main__":
    main()
