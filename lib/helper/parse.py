#-*- encoding:utf-8 -*-
__author__ = "QIUEER"
__date__ = "20170503"

import ConfigParser
from lib.base.scolor import scolor
from lib.base.sstr import sstr

class BUp(ConfigParser.SafeConfigParser):
    
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

    def list_one(self, section):
        if self.has_section(section) == False:return
        shper = sstr()
        conf = self.get_section_dict(section)
        scolor.info(u"################# [ section: %s ]" % (section))
        keymap = self._key_map
        max_key_len = self._max_key_len if self._max_key_len else 12
        for k in self._key_order:
            key_cn = keymap.get(k, "None")
            val = conf.get(k, None)
            print u"{0}".format(shper.str_rpad(key_cn, width=max_key_len) + ": " + str(val))

    def list(self):
        sections = self.sections()
        for sec in sections:
            self.list_one(sec)
