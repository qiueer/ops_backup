#-*- encoding:utf-8 -*-
'''
author: qiueer
date: 20161217
'''
import traceback

class sstr(object):
    def _is_chinese(self, uchar):
        """判断一个unicode是否是汉字"""
        if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
            return True
        else:
            return False

    def _str_pad(self, text, width=12, fill=" ", direction="r"):
        if direction not in ['l', 'r']: return text
        stext = str(text)
        utext = stext.decode("utf-8")
        cn_count = 0
        for u in utext:
            if self._is_chinese(u):
                cn_count += 1
        resstr = u""
        if direction == "r":
            resstr = fill * (width - cn_count - len(utext)) + stext
        if direction == "l":
            resstr = stext+fill * (width - cn_count - len(utext))
        return u"{0}".format(resstr)
    
    def str_lpad(self, text,width=12, fill=" "):
        return self._str_pad(text, width=width, fill=fill, direction="l")
    
    def str_rpad(self, text,width=12, fill=" "):
        return self._str_pad(text, width=width, fill=fill, direction="r")
    
    def _get_right_content(self, content):
        try:
            content = content.encode("utf8")
        except Exception:
            try:
                content = content.encode("gbk")
            except Exception:
                try:
                    content = content.encode("GB2312")
                except Exception:
                    pass
        return content
    
    def dictstr(self, width=12, fill=u"", **kwargs):
        '''
        kwargs: dict类型，如果包含orders，则按orders的先后顺序
        '''
        try:
            order_keys = []
            if kwargs.has_key("orders") == True:
                order_keys = kwargs["orders"]
            if kwargs.has_key("orders"):
                del(kwargs["orders"]) 
            msgstr = u""
            if order_keys:
                for key in order_keys:
                    if not kwargs.has_key(key): continue
                    val = kwargs[key]
                    key = self.str_rpad(key, width)
                    key = unicode(key, "UTF-8")
                    msgstr = u"%s%s: %s\n" % (msgstr, key, self._get_right_content(val))
            for (key, val) in kwargs.iteritems():
                if kwargs.has_key(key) and key not in order_keys:
                    val = kwargs[key]
                    key = self.str_rpad(key, width)
                    key = unicode(key, "UTF-8")
                    msgstr = u"%s%s: %s\n" % (msgstr, key, self._get_right_content(val))
            msgstr = str(msgstr).rstrip()
            msgstr = self._get_right_content(msgstr)
            return msgstr
        except Exception,expt:
            print traceback.format_exc()
            return None