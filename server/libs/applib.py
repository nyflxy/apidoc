__author__ = 'niyoufa'

import pdb
import os
import sys
import tornado
import tornado.web
import tornado.httpserver
from tornado.options import options, define

_root = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(_root))
import server.cache as rediscache
from server.libs import asynclib
async_utils = asynclib.AsyncUtils()

try:
    parse_options_flag = True
    from libs.options import parse_options
except:
    parse_options_flag = False
    from server.libs.options import parse_options

class Application(tornado.web.Application):
    def __init__(self,handlers):
        settings = dict(
            debug=options.DEBUG,
            template_path=_root + "/templates",
            static_path=_root + "/static",
            cookie_secret="2379874hsdhf0234990sdhsaiuofyasop977djdj",
            xsrf_cookies=False,
            pycket={
            'engine': 'redis',
            'storage': {
                'host': options.REDIS_HOST,
                'port': options.REDIS_PORT,
                'db_sessions': 10,
                'db_notifications': 11,
                'max_connections': 2 ** 31,
            },
            'cookies': {
                # 设置过期时间
                'expires_days': 7,
                # 'expires':None, #秒
            },
        }
        )
        super(Application, self).__init__(handlers,**settings)
        self.executor = tornado.concurrent.futures.ThreadPoolExecutor(16)

def main(handlers,port=7000):
    if "module_name" not in options:
        parse_options()
    app = Application(handlers=handlers)
    http_server = tornado.httpserver.HTTPServer(app)
    if "port" in options and options.port :
        port = options.port
    print("\nserver start !")
    print("port:%s\n" % port)
    http_server.bind(port)
    http_server.start()
    async_utils.cmd(rediscache.init_cache)
    tornado.ioloop.IOLoop.instance().start()
