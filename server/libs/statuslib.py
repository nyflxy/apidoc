_author="niyoufa"

import sys
from tornado.options import options

class Status(object):

    def __setattr__(self, key, value):
        if key in self.__dict__.keys():
            raise (self.StatusError, "Changing Status.%s" % key)
        else:
            self.__dict__[key] = value
            for v in value:
                self.__dict__["%s_%s"%(key,v[0].upper())] = v[1]

    def __getattr__(self, key):
        if key in self.__dict__:
            return self.key
        else:
            return None

status = Status()
sys.modules[__name__] = status
