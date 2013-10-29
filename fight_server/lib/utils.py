# -*- coding: utf-8 -*-
from twisted.python import log
import sys
import time
import traceback
import types

def merge_settings(orig, new):
    for name in dir(new):
        if name.upper() == name:
            setattr(orig, name, getattr(new, name))

def dump_settings(settings):
    print "settings {"
    for name in sorted(dir(settings)):
        if name.upper() == name:
            print "  %s = %r" % (name, getattr(settings, name))
    print "}"

class LogMixin(object):
    def msg(self, *args, **kwargs):
        kwargs.setdefault("system", self)
        log.msg(*args, **kwargs)

    def err(self, *args, **kwargs):
        kwargs.setdefault("system", self)
        log.err(*args, **kwargs)

def strdump(s, n_hex=8, n_repr=12):
    """显示字符（十六进制 | repr）
    """
    if not s:
        return ""
    l = ["%02x" % c for c in bytearray(s[:n_hex])]
    l.extend(["|", repr(s[:n_repr])])
    return " ".join(l)

def exc_info():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = ["{}: {}\n".format(exc_type, exc_value)]
    lines.extend(traceback.format_tb(exc_traceback))
    return "".join(lines)

def cutit(s, max_length=80):
    if not isinstance(s, basestring):
        s = str(s)
    if max_length and len(s) > max_length:
        return s[:max_length] + ".(%d)." % (len(s) - max_length)
    return s

def asbool(s):
    if isinstance(s, types.StringTypes):
        return s.lower() in ("yes", "y", "true", "t", "1")
    return bool(s)

def asint(s, base=10):
    try:
        return int(s, base)
    except:
        return 0

def strtime(t=None):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
