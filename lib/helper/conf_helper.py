#-*- encoding:utf-8 -*-
'''
author: qiueer
date: 20161217
update: 20161225, add check function
'''

import ConfigParser
import traceback
import types
import sys
from lib.base.scolor import scolor
from lib.base.sstr import sstr

class conf_helper(ConfigParser.SafeConfigParser):
    
    def __init__(self, conffile, key_map=dict(), key_check=dict(), key_order=[], max_key_len=12):
        #super(BUpConfig,self).__init__()
        ConfigParser.SafeConfigParser.__init__(self)
        self._conffile = conffile
        self._key_map = key_map if key_map else dict() ## key与key_cn的对应关系，用dict表示
        self._key_check = key_check if key_check else dict() ## key与key所对应值的校验函数的对应关系，用dict表示
        self._key_order = key_order if key_order else [] ## key输入输出的顺序
        self._max_key_len = max_key_len ## 最长key的长度是多少，用于格式化对齐输出
        self.read(self._conffile)
        
    def get_section_dict(self, section):
        if self.has_section(section) == False: return dict()
        items = self.items(section)
        conf = dict()
        for k,v in items:
            conf[k] = v
        return conf
    
    def save(self):
        self.write(open(self._conffile, "w"))
        
    def _get_key_val(self, k, old_val=None):
        keymap = self._key_map
        key_cn = keymap.get(k, "Not_Assign")
        is_continue = True
        while is_continue == True:
            val = raw_input(key_cn+": ")
            if val == "": val = old_val  ## 如果不输入任何值，则用旧值作为默认值，适用于修改数据的情况，避免校验失败
            check_func = self._key_check.get(k,None)
            if not check_func:
                return val
            if check_func and type(check_func) == types.FunctionType:
                (is_check_ok, msg) = check_func(val)
                if is_check_ok == True:
                    return val
                else:
                    scolor.error("参数校验失败，信息：%s" % (msg))
                    while True:
                        resp = raw_input(u"是否继续? (y or n) ")
                        if str(resp).strip().lower() in ["n","no"]:
                            is_continue = False
                            break
                        elif str(resp).strip().lower() in ["y","yes"]:
                            break
        return None
                            
    def list_one(self, section):
        if self.has_section(section) == False:return False
        shper = sstr()
        conf = self.get_section_dict(section)
        scolor.info("################# [ section: %s ]" % (section))
        keymap = self._key_map
        max_key_len = self._max_key_len if self._max_key_len else 12
        for k in self._key_order:
            key_cn = keymap.get(k, "None")
            val = conf.get(k, None)
            print shper.str_rpad(key_cn, width=max_key_len) + ": " + str(val)

    def list(self):
        sections = self.sections()
        for sec in sections:
            self.list_one(sec)
    
    def delete(self, section, tip=""):
        if self.has_section(section) == False:
            scolor.warn(u"SECTION不存在: %s"%(section))
            return False
        self.list_one(section)

        try:
            while True:
                resp = raw_input(u"是否确认删除SECTION为:%s的配置? (y or n) " % (section))
                if str(resp).strip().lower() in ["n","no"]:
                    break
                elif str(resp).strip().lower() in ["y","yes"]:
                    self.remove_section(section)
                    self.save()
                    break
        except:
            pass
        
    def modify(self, section):
        if self.has_section(section) == False:
            scolor.info("SECTION不存在: %s"%(section))
            return
        self.list_one(section)
    
        try:
            #keymap = self._key_map
            val_map = dict()
            for k in self._key_order:
                old_val = self.get_section_dict(section).get(k)
                val = self._get_key_val(k, old_val=old_val)
                if not val: val = ""
                val_map[k] = val

            while True:
                resp = raw_input(u"是否确认修改? (y or n) ")
                if str(resp).strip().lower() in ["n","no"]:
                    break
                elif str(resp).strip().lower() in ["y","yes"]:
                    for k in self._key_order:
                        if val_map[k]:self.set(section, k, val_map[k])
                    self.save()
                    break
        except:
            print traceback.format_exc()

    def add(self):
        try:
            section = raw_input(u"SECTION名(英文唯一标识): ")
            
            if self.has_section(section) == True:
                scolor.error("SECTION名已存在: %s"%(section))
                self.list_one(section)
                return False
                
            val_map = dict()
            for k in self._key_order:
                val = self._get_key_val(k)
                if not val: val = ""
                val_map[k] = val
                            
            while True:
                resp = raw_input(u"是否确认增加? (y or n) ")
                if str(resp).strip().lower() in ["n","no"]: break
                if str(resp).strip().lower() in ["y","yes"]:
                    self.add_section(section)
                    for k in self._key_order: self.set(section, k, val_map[k])
                    self.save()
                    break
        except:
            print traceback.format_exc()
