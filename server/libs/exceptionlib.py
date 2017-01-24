_author="niyoufa"

import pdb
from tornado.web import HTTPError

# 用户输入异常
class CustomException(Exception):

    def __init__(self,error_info):
        self.err = (2, error_info)

class TokenException(Exception):

    def __init__(self,error_info):
        self.err = (3, error_info)

# 抛出异常测试函数
def raiseTest():
    # 抛出异常
    raise CustomException("用户输入异常")

class MissingArgumentError(HTTPError):
    """Exception raised by `RequestHandler.get_argument`.

    This is a subclass of `HTTPError`, so if it is uncaught a 400 response
    code will be used instead of 500 (and a stack trace will not be logged).

    .. versionadded:: 3.1
    """
    def __init__(self, arg_name):
        super(MissingArgumentError, self).__init__(
            400, '缺少参数 %s' % arg_name)
        self.arg_name = arg_name


# 主函数
if __name__ == '__main__':
    try:
        raiseTest()
    except CustomException as msg:
       print(msg.err)