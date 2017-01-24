__author__ = "niyoufa"

import os
import time
import traceback
import logging

logger = logging.getLogger("exception")

_root = os.path.dirname(os.path.dirname(__file__))

from server.libs import exceptionlib

# 初始化返回参数
def init_response_data():
    result = {'code': 0, 'msg': '返回成功', 'data': {}}
    return result


# 重置返回参数
def reset_response_data(info, code=1):
    result = {'code': code, 'msg': str(info), 'data': {}}
    return result


# 异常处理装饰器 同步
def exception_handler(func):
    def handler(self,*args,**kwargs):
        try:
            func(self,*args,**kwargs)
        except exceptionlib.CustomException as msg:
            code = msg.err[0]
            info = msg.err[1]
            result = reset_response_data(info, code)
            self.finish(result)
        except:
            info = traceback.format_exc()
            result = reset_response_data(info)
            logger.error(info)
            self.finish(result)
    return handler

# 异常处理装饰器 异步
def async_exception_handler(func):

    def handler(self,*args,**kwargs):
        try:
            self._auto_finish = False
            future = func(self,*args,**kwargs)
            if future and future.exc_info():
                raise Exception(future.result())
        except exceptionlib.CustomException as msg:
            info = msg.err[1]
            result = reset_response_data(info)
            self.finish(result)
        except:
            info = traceback.format_exc()
            result = reset_response_data(info)
            logger.error(info)
            self.finish(result)
    return handler