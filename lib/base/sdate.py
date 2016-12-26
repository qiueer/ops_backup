#-*- encoding:utf-8 -*-

import re
import datetime
import time

class TZ(datetime.tzinfo):
    def __init__(self, tzstr=None):
        self._prefix = "GMT"
        self._flag = "+"
        self._hours = 8
        if tzstr != None:
            tzstr = tzstr.upper().replace(" ", "").strip()
            m = re.match(r"^(GMT|UTC)(-|\+)(\d{1,2})", tzstr)
            if m != None:
                (self._prefix, self._flag, self._hours)  = m.group(1, 2, 3) 
                self._hours = int(self._hours)
            elif tzstr in ["GMT", "UTC"]:
                self._prefix = tzstr
                self._flag = ""
                self._hours = 0
                self._tzstr = tzstr
            else:
                self._prefix = "GMT"
                self._flag = "+"
                self._hours = 8
            
            self._tzstr = "%s%s%s" % (self._prefix, self._flag, self._hours)
            if tzstr in ["GMT", "UTC"]:
                self._tzstr = tzstr

        
    def utcoffset(self, dt):
        hour = self._hours
        flag = self._flag
        if flag == "-":
            hour = -1 * hour
        return datetime.timedelta(hours=hour)
      
    def dst(self, dt):
        hour = self._hours
        flag = self._flag
        if flag == "-":
            hour = -1 * hour
        return datetime.timedelta(hours=hour)
    
    def tzname(self, dt):
        return self._tzstr

class sdate(object):
    def __init__(self, days = 0, hours=0, minutes=0, seconds=0, tzstr="GMT+8"):
        '''
        time offset here 
        include days, hours, minutes, seconds
        '''
        self.reset(days=days, hours=hours, minutes=minutes, seconds=seconds, tzstr=tzstr)

    def reset(self, days = 0, hours=0, minutes=0, seconds=0, tzstr="GMT+8"):
        self._days = days
        self._hours = hours
        self._minutes = minutes
        self._seconds = seconds
        self._tzstr = tzstr
        self._dt = datetime.datetime.now(TZ(tzstr=self._tzstr)) + datetime.timedelta(days=self._days,hours=self._hours, minutes=self._minutes,seconds=self._seconds)
        return self

    def tzname(self):
        return self._dt.tzname()

    def year(self):
        return self._dt.year

    def month(self):
        return self._dt.month
   
    def day(self):
        return self._dt.day
   
    def hour(self):
        return self._dt.hour
   
    def minute(self):
        return self._dt.minute
   
    def weekofday(self):
        return self._dt.weekday()
    
    def second(self):
        return self._dt.second
    
    def microsecond(self):
        return self._dt.microsecond
    
    def datetime(self):
        return self._dt.strftime("%Y%m%d%H%M%S")
    
    def datetime_ex(self):
        return "%s%s" % (self._dt.strftime("%Y%m%d%H%M%S"), int(self.microsecond()/1000))
    
    def datetime_human(self):
        return self._dt.strftime("%Y-%m-%d %H:%M:%S")
    
    def date(self):
        return self._dt.strftime("%Y-%m-%d")
    
    def time(self):
        return self._dt.strftime("%H:%M:%S")
    
    def unix_timestamp(self):
        return int(time.mktime(self._dt.timetuple()))
    
    def iso8601(self):
        '''
        NOT include: microsecond and time zone info
        '''
        dtstr = datetime.datetime(self.year(), self.month(), self.day(), self.hour(), self.minute(),self.second()).isoformat()
        return dtstr

    def iso8601_ms(self):
        '''
        include microsecond but not time zone info
        '''
        dtstr =  datetime.datetime.isoformat(self._dt)
        return dtstr
    
    def iso8601_tz(self):
        '''
        include: time zone info
        '''
        dtstr = datetime.datetime(self.year(), self.month(), self.day(), self.hour(), self.minute(),self.second(), 0, TZ(tzstr=self._tzstr)).isoformat()
        return dtstr
    
    def iso8601_ms_tz(self):
        '''
        include: microsecond and time zone info
        '''
        dtstr = datetime.datetime(self.year(), self.month(), self.day(), self.hour(), self.minute(),self.second(), self.microsecond(), TZ(tzstr=self._tzstr)).isoformat()
        return dtstr
    
    def from_unix_timestamp(self, unix_timestamp, tzstr="GMT+8"):
        self._dt = datetime.datetime.fromtimestamp(unix_timestamp, TZ(tzstr=tzstr))
        self._tzstr = tzstr
        return self
    
    def from_datatime_str(self, string, fmt, tzstr="GMT+8"):
        self._dt = datetime.datetime.strptime(string, fmt)
        self._tzstr = tzstr
        return self

    def __repr__(self):
        return self.__str__()

    def __unicode__(self):
        return self.__str__()
    
    def __str__(self):
        dtinfo = {
            "tzname": self.tzname(),
            "year":self.year(),
            "month":self.month(),
            "weekday": self.weekofday(),
            "day":self.day(),
            "hour":self.hour(),
            "minute":self.minute(),
            "second":self.second(),
            "microsecond": self.microsecond(),
            "datetimestr": self.datetime_str(),
            "datetime": self.datetime(),
            "date": self.date(),
            "time": self.time(),
            "unix_timestamp": self.unix_timestamp(),
            "iso8601": self.iso8601(),
            "iso8601_ms": self.iso8601_ms(),
            "iso8601_tz": self.iso8601_tz(),
            "iso8601_ms_tz": self.iso8601_ms_tz(),
        }
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        return pp.pformat(dtinfo)

