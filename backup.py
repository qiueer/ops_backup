#!/usr/bin/env python
# -*- encoding=utf-8 -*-
###
###

import sys
import os
import re
import traceback
from optparse import OptionParser

from lib.base.slog import slog
from lib.base.scolor import scolor
from lib.base.sdate import sdate
from lib.base.cmds import cmds
from lib.base.sstr import sstr
from lib.helper.conf_helper import conf_helper

try:
    import readline
    import atexit
    import codecs
except Exception:
    pass


reload(sys) 
sys.setdefaultencoding('utf8')
histfile = os.path.join(os.environ["HOME"], ".backup")

def get_realpath():
    return os.path.split(os.path.realpath(__file__))[0]

def get_binname():
    return os.path.split(os.path.realpath(__file__))[1]

def backup_one(conffile, input_section, debug=False):
    bc = conf_helper(conffile)
    itemconf = bc.get_section_dict(input_section)
    srcdir = itemconf.get("srcdir", None)
    destdir = itemconf.get("destdir", None)
    brange = itemconf.get("range", None)
    files = itemconf.get("files", None)
    logger = slog("/tmp/backup.log", debug=debug)
    if bc.has_section(input_section) == False:
        scolor.info("备份标识不存在: %s"%(input_section))
        return
    logobj = {
              u"备份标识": input_section,
              u"备份目录": srcdir,
              u"存储目录": destdir,
              u"范围(包含or不包含)": brange,
              u"文件(夹)列表": files,
              u"orders": [u"section", u"备份目录", u"存储目录", u"范围(包含or不包含)"]
    }
    logger.dictlog(level="info", width=20, **logobj)
    
    scolor.info(u"尝试执行备份任务，备份信息如下: ")
    scolor.info(u"===============================")
    print sstr().dictstr(width=20, **logobj)

    try:
        ## src dir
        srcdir = str(srcdir).strip()
        while '//' in str(srcdir):srcdir=str(srcdir).replace('//', '/')
        while str(srcdir).endswith('/'):srcdir=srcdir[:-1]
        pos = str(srcdir).rfind('/')
        dirroot = srcdir[:pos] ##
        dirname = srcdir[pos+1:] ## relative dir name

        ## dest dir
        destdir = str(destdir).strip()
        while '//' in str(destdir):destdir=str(destdir).replace('//', '/')
        while str(destdir).endswith('/') and len(destdir) > 2:destdir=destdir[:-1]
        
        if os.path.exists(srcdir) == False or os.path.exists(destdir) == False:
            scolor.error(u"=> 备份任务")
            infobj = {
                      u"状态": u"失败",
                      u"错误": u"备份目录或存储目录不存在",
                      u"备份目录": srcdir,
                      u"存储目录": destdir,
                      u"orders": [u"状态", u"错误", u"备份目录", u"存储目录"]
            }
            scolor.error(sstr().dictstr(width=8, **infobj))
            return
        
        if str(brange).lower().strip() not in ["include", "exclude"]:
            scolor.error(u"=> 备份任务")
            infobj = {
                      u"状态": u"失败",
                      u"错误": u"备份范围错误，只能是include或exclude",
                      u"orders": [u"状态", u"错误"]
            }
            scolor.error(sstr().dictstr(width=4, **infobj))
            return

        ## include or exclude files
        files = str(files).strip()
        files_ary = re.split("[ |,|;]+", files)
        last_files = []
        if files_ary:
            for each_file in files_ary:
                if not each_file:continue
                while '//' in str(each_file):each_file=str(each_file).replace('//', '/')
                while str(each_file).endswith('/'):each_file=each_file[:-1]
                while str(each_file).startswith('/'):each_file=each_file[1:]
                each_file = each_file.replace(" ", "")
                last_files.append(each_file)

        nowdt = sdate().datetime()
        nd = sdate().date()
        tarname = "%s_%s.tar.gz " % (dirname, nowdt)
        tmpfile = "/tmp/%s" % (tarname)
        last_destdir = "%s/%s/" % (destdir, nd)
        subffix = ""
        tar_cmdstr = ""
        if str(brange).lower().strip() == "include":
            for ef in last_files:
                subffix = subffix+ dirname + "/" + ef+" "
            if str(subffix).strip() == "": ## 备份整个目录
                tar_cmdstr = "cd %s && tar czf %s %s" % (dirroot, tmpfile, dirname)
            else:  ## 备份指定的目录
                tar_cmdstr = "cd %s && tar czf %s %s" % (dirroot, tmpfile, subffix)
            
        if str(brange).lower().strip() == "exclude":
            for ef in last_files:
                subffix = subffix + "--exclude=" + dirname + "/" + ef +" "
            tar_cmdstr = "cd %s && tar czf %s %s %s" % (dirroot, tmpfile, dirname, subffix)

        c1 = cmds(tar_cmdstr, timeout=1800)
        stdo1 = c1.stdo()
        stde1 = c1.stde()
        retcode1 = c1.code()
        logobj = {
                  u"命令": tar_cmdstr,
                  u"标准输出": stdo1,
                  u"错误输出": stde1,
                  u"返回码": retcode1,
                  u"orders": [u"命令", u"标准输出", u"错误输出", u"返回码"]
        }
        logger.dictlog(level="info", width=12, **logobj)
        
        ## 打包归档失败
        if retcode1 != 0:
            scolor.error(u"=> 备份任务")
            infobj = {
                      u"状态": u"失败",
                      u"错误": u"打包归档失败，具体：%s" % (stde1),
                      u"orders": [u"状态", u"错误"]
            }
            scolor.error(sstr().dictstr(width=4, **infobj))
            return
        
        #cmdstr = "mkdir -p %s && mv %s %s && rm -frv %s" % (last_destdir, tmpfile, last_destdir, tmpfile)
        cmdstr = "mkdir -p %s && mv -v %s %s" % (last_destdir, tmpfile, last_destdir)
        c2 = cmds(cmdstr)
        stdo2 = c2.stdo()
        stde2 = c2.stde()
        retcode2 = c2.code()
        logobj = {
                  u"命令": cmdstr,
                  u"标准输出": stdo2,
                  u"错误输出": stde2,
                  u"返回码": retcode2,
                  u"orders": [u"命令", u"标准输出", u"错误输出", u"返回码"]
        }
        logger.dictlog(level="info", width=12, **logobj)
        if retcode2 != 0:
            scolor.error(u"=> 备份任务")
            infobj = {
                      u"状态": u"失败",
                      u"错误": u"创建目录或移动文件失败，具体：%s" % (stde1),
                      u"orders": [u"状态", u"错误"]
            }
            scolor.error(sstr().dictstr(width=4, **infobj))
            return

        scolor.info(u"=> 备份任务")
        infobj = {
                  u"状态": u"成功",
                  u"原目录": srcdir,
                  u"备份位置": "%s%s" % (last_destdir, tarname) ,
                  u"orders": [u"状态", u"原目录"]
        }
        scolor.info(sstr().dictstr(width=8, **infobj))
    except:
        print traceback.format_exc()

def backup_all(conffile, debug=False):
    bc = conf_helper(conffile)
    sections = bc.sections()
    for sc in sections:
        backup_one(conffile, sc, debug=debug)
        
def is_dir_exist(dirpath):
    if os.path.exists(dirpath) == False:
        return False,"目录%s不存在" %(dirpath)
    return True,""

def is_range_ok(rangestr):
    if str(rangestr).strip() not in ["include", "exclude"]:
        return (False, u"值只能是include或exclude")
    return True,""

def main():
    try:
        parser = OptionParser()
        parser.add_option("-c", "--conf",  
                  action="store", dest="conf", default=None,  
                  help="configure file", metavar="${backup_conf_file}")
        parser.add_option("-l", "--list", dest="list", default=False,
                  action="store_true", help="list all the configure")
        parser.add_option("-a", "--add", dest="add", default=False,
                  action="store_true", help="add configure to config file")
        parser.add_option("-m", "--modify", dest="modify", default=False,
                  action="store_true", help="modify backup configure to config file")
        parser.add_option("-d", "--delete", dest="delete", default=False,
                  action="store_true", help="delete backup configure from config file")
        parser.add_option("-D", "--debug", dest="debug", default=False,
                  action="store_true", help="if open debug module")
        parser.add_option("-q", "--quiet", dest="quiet", default=False,
                  action="store_true", help="quiet,only for backup all,if true,do not ask to make sure")
        parser.add_option("-s", "--section",  
                          action="store", dest="section", default=None,  
                          help="which section to backup, if none, backup all", metavar="${section}")

        (options, args) = parser.parse_args()
        list_flag = options.list
        conffile = options.conf
        add_flag = options.add
        modify_flag = options.modify
        delete_flag = options.delete
        debug_flag = options.debug
        quiet = options.quiet
        input_section = options.section
        
        if not conffile:
            conffile = get_realpath() + "/etc/backup.conf"

        if os.path.exists(conffile) == False:
            conffile = "/etc/backup.conf"
            if os.path.exists(conffile) == False:
                parser.print_help()
                sys.exit(1)
                
        tmp_list = [list_flag, add_flag, modify_flag, delete_flag]
        cnt = 0
        for a in tmp_list:
            if a == True: cnt += 1
            
        if cnt > 1:
            parser.print_help()
            sys.exit(1)
            
        key_map = {"srcdir": u"备份目录", "destdir": u"存储目录", "range": u"备份范围", "files":u"包含或排除的文件(夹)"}
        key_order = ["srcdir", "range", "files", "destdir"]
        key_check = {"srcdir": is_dir_exist, "destdir": is_dir_exist, "range": is_range_ok}
        chp = conf_helper(conffile, key_map=key_map, key_check=key_check, key_order=key_order, max_key_len=20)
        ## backup the input section
        if input_section and (list_flag or add_flag or modify_flag or delete_flag) == False:
            backup_one(conffile, input_section, debug=debug_flag)

        if not input_section and (list_flag or add_flag or modify_flag or delete_flag) == False:
            if quiet == True:
                backup_all(conffile, debug=debug_flag)
		return
            else:
                while True:
                    resp = raw_input(u"是否确定所有的备份操作? (y or n) ")
                    if str(resp).strip().lower() in ["n","no"]:
                        return
                    elif str(resp).strip().lower() in ["y","yes"]:
                        backup_all(conffile, debug=debug_flag)
                        return

        ## list all
        if list_flag == True and not input_section:
            chp.list()
            return
        
        ## list one
        if  list_flag == True and input_section:
            chp.list_one(input_section)
            return
        
        ## delete one
        if delete_flag and input_section:
            chp.delete(input_section)
            return
        
        ## modify one
        if modify_flag and input_section:
            chp.modify(input_section)
            return

        ## add one
        if add_flag and not input_section:
            chp.add()
            return
        
        parser.print_help()
        
    except Exception, expt:
        print traceback.format_exc()
        
if __name__ == "__main__":
    main()
