__author__ = "niyoufa"

import pdb
import logging
import traceback
import tornado
from tornado.ioloop import IOLoop
from tornado.concurrent import run_on_executor
import functools
import tornado.ioloop
import tornado.web
from concurrent.futures import ThreadPoolExecutor

from server.libs import exceptionlib

logger = logging.getLogger("exception")

# EXECUTOR = ThreadPoolExecutor(max_workers=4)#全局线程池

# 重置返回参数
def reset_response_data(info, code=1):
    result = {'code': code, 'msg': str(info), 'data': {}}
    return result

class AsyncUtils(object):
    def __init__(self,num_worker=8):
        self.io_loop = IOLoop.current()
        self.executor = ThreadPoolExecutor(num_worker)

    @run_on_executor
    def cmd(self,func, *args, **kwargs):
        res = func(*args,**kwargs)
        return res

    def unblock(self,http_method):
        #必须添加该装饰器，表明当前方法结束后，并不finish该请求
        #Tornado请求执行的流程默认是: initialize()->prepare()->http_method(get/post等)->finish()
        #当用unblock装饰器装饰后，http_method实际是执行下面的_wrapper()方法，在_wrapper中我们只是将原始的
        #http_method提交给线程池处理，所以还没有执行完该http_method，所以还不能finish该请求
        @tornado.web.asynchronous
        @functools.wraps(http_method)
        def _wrapper(handler_self, *args, **kwargs):
            #以下的callback必须在主线程执行
            #self.write(),self.finish()等都不是线程安全的
            # 直接在handler中return，该结果即future.result(), 后续将被self.write(result)
            #         #不要在子线程中执行self.write(),因为这并非线程安全的方法
            #         #通过ioloop.IOLoop.instance().add_callback的方式，将其交给主线程执行
            # ioloop提供的add_callback是线程安全的
            def callback(future):
                if future.exception():
                    try:
                        raise Exception(future.result())
                    except exceptionlib.CustomException as msg:
                        code = msg.err[0]
                        info = msg.err[1]
                        result = reset_response_data(info,code)
                        logger.error(result)
                        handler_self.finish(result)
                    except:
                        info = traceback.format_exc()
                        result = reset_response_data(info)
                        logger.error(result)
                        handler_self.finish(result)
                else:
                    handler_self.finish(future.result())

            _future = self.executor.submit(
                functools.partial(http_method, handler_self, *args, **kwargs)
            )
            tornado.ioloop.IOLoop.instance().add_future(_future, callback)
        return _wrapper
