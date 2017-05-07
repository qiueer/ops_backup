#-*- encoding:utf-8 -*-

import platform
import datetime
import os
import time
import signal

from subprocess import PIPE, Popen
import threading
import traceback
import select

try:
    import fcntl
except:
    pass

class cmds(threading.Thread):
    
    def __init__(self, cmdstr, env=None, cwd=None, stdout=PIPE, stderr=PIPE, timeout=None, debug=False):
        threading.Thread.__init__(self)
        ## in
        self._cmdstr = cmdstr
        self._env = env
        self._cwd = cwd
        self._stdout = stdout
        self._stderr = stderr
        self._timeout = timeout
        self._debug = debug
        
        ## out
        self.ps = None
        self.stdout = None
        self.stderr = None
        self.retcode = 0
        self.is_done = False
        self.is_timeout = False
        
    def done(self):
        return self.is_done
    
    def timeout(self):
        return self.is_timeout
    
    def no_block_read(self, output):
        fd = output.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        try:
            return output.read()
        except:
            return None
             
    def run(self):
            if platform.system() == "Linux":
                    self.ps = Popen(self._cmdstr, env=self._env, cwd=self._cwd, stdout=self._stdout, stdin=PIPE, stderr=self._stderr, shell=True)
            else:
                    self.ps = Popen(self._cmdstr, env=self._env, cwd=self._cwd, stdout=self._stdout, stdin=PIPE, stderr=self._stderr, shell=False)

            start = datetime.datetime.now()
            while self.ps.poll() is None:
                time.sleep(0.2)

                if platform.system() == "Linux":
                    infds,outfds,errfds = select.select([self.ps.stdout,], [self.ps.stderr, ], [], 5)
                    if len(infds) != 0:
                        tmp_str = self.no_block_read(infds[0])
                        self.stdout = "{0}{1}".format(self.stdout if self.stdout != None else "", tmp_str)
                        if self._debug:print tmp_str,
                    if len(outfds) != 0:
                        tmp_str = self.no_block_read(outfds[0]),
                        self.stderr = "{0}{1}".format(self.stderr if self.stderr != None else "", tmp_str)
                        if self._debug: print tmp_str,
                        
                now = datetime.datetime.now()
                if self._timeout and (now - start).seconds > self._timeout:
                    os.kill(self.ps.pid, signal.SIGINT)
                    self.retcode = -1
                    self.is_done = True
                    self.is_timeout = True
                    break
                
            if platform.system() == "Windows":
                kwargs = {'input': self.stdout}
                (self.stdout, self.stderr) = self.ps.communicate(**kwargs)
                self.retcode = self.ps.returncode

            self.is_done = True

    def __repr__(self):
        return self.stdo()

    def __unicode__(self):
        return self.stdo()
    
    def __str__(self):
        try:
            import simplejson as json
        except:
            import json
        res = {"stdout":self.stdout, "stderr": self.stderr, "retcode": self.retcode}
        return  json.dumps(res, separators=(',', ':'), ensure_ascii=False).encode('utf-8') 
    
    def stdo(self):
        if self.stdout:
            return self.stdout.strip().decode('UTF-8')
        return ''
    
    def stde(self):
        if self.stderr:
            return self.stderr.strip().decode('UTF-8')
        return ''
    
    def code(self):
        return self.retcode
    
    def feedback(self):
        ## 阻塞
        while True:
            if self.timeout() or self.done():
                return (self.stdo(), self.stde(), self.code())