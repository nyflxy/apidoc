_author="niyoufa"

import time
import datetime
import hashlib
import os
import sys
import pymongo
import math
import logging

mongo_client = pymongo.MongoClient("localhost", 27017)

_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.join(_root))
libs_path = _root + "/server/libs"
sys.path.append(libs_path)

from server.libs.bson import objectid

# 初始化返回参数
def init_response_data():
    result = {'code': 0, 'msg': '返回成功', 'data': {}}
    return result

# 重置返回参数
def reset_response_data(info):
    result = {'code': 1, 'msg': str(info), 'data': {}}
    return result

# 时间戳转化成日期 2016-11-08
def timestamp2date(timestamp):
    timestamp = int(timestamp)
    time_arry = time.localtime(timestamp)
    date = time.strftime("%Y-%m-%d", time_arry)
    return date

# 时间戳转化成日期 201611081010
def timestamp2date_minute(timestamp):
    """
    时间戳转化成日期 转换到分钟
    :param timestamp: 毫秒数 （自1970年)
    :return:
    """
    timestamp = int(timestamp/1000)
    time_arry = time.localtime(timestamp)
    date = time.strftime("%Y-%m-%d %H:%M", time_arry)
    date_minute = date.replace("-","").replace(":","").replace(" ","")
    return date_minute

# 时间字符串转datetime
def strtodatetime(datestr,format):
    return datetime.datetime.strptime(datestr,format)

# datetime转时间戳毫秒数
def datetime2timestamp(datetime_obj):
    if type(datetime_obj) != datetime.datetime:
        raise Exception("时间格式错误， 必须是datetime.datetime对象")
    return time.mktime(datetime_obj.timetuple())

def format_content(content):
    content = content.replace("\n","<br/>")
    return content

def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        return True
    else:
        return False

def is_chinese_string(ustring):
    """判断一个字符串是否包含汉字"""
    flag = False
    res_map = map(is_chinese,ustring)
    for obj in res_map:
        if obj == True:
            flag = True
            break
    return flag

def is_url(url_string):
    if not (url_string.startswith("http://") or  url_string.startswith("https://")):
        return False
    return True

def create_objectid(obj_id):
    _id = objectid.ObjectId(obj_id)
    return _id

def md5(mingwen):
    m = hashlib.md5()
    mdr_str = mingwen.encode()
    m.update(mdr_str)
    ciphertext = m.hexdigest()
    return ciphertext

def check_api_access(app_id, call_time, key):
    # 验证时间
    call_time = int(call_time)
    curr_time = int(time.time() * 1000)
    if curr_time - call_time > 3600*1000:
        return False
    app_coll = mongo_client["auth"]["client"]
    app_obj = app_coll.find_one({
        "identifier":app_id,
        "is_enable":True,
    })
    if not app_obj:
        return False
    secret = app_obj.get("secret")
    access_key = md5(app_id+secret+str(call_time))
    if not access_key == key:
        return False
    else:
        return True

# 计算分页信息
def count_page(length, page, page_size=15, page_show=10):
    page = int(page)
    page_size = int(page_size)
    length = int(length)
    if length == 0:
        return {"enable": False,
                "page_size": page_size,
                "skip": 0}
    max_page = int(math.ceil(float(length) / page_size))
    page_num = int(math.ceil(float(page) / page_show))
    pages = list(range(1, max_page + 1)[((page_num - 1) * page_show):(page_num * page_show)])
    skip = (page - 1) * page_size
    if page >= max_page:
        has_more = False
    else:
        has_more = True
    pager = {
        "page_size": page_size,
        "max_page": max_page,
        "pages": pages,
        "page_num": page_num,
        "skip": skip,
        "page": page,
        "enable": True,
        "has_more": has_more,
        "total":length,
    }
    return pager

# 获取请求时间参数
def format_time_request_params(start_time, end_time, mode=0, time_string_format='%Y-%m-%d %H:%M:%S', compare_mode=0):
    """
    获取请求时间参数
    :param start_time: 开始时间
    :param end_time: 结束时间
    :param mode: 模式 0：用户手动输入 1:选择模式
    :param time_string_format: 时间格式化格式
    :param compare_mode: 比较模式 0：时间毫秒数 1:时间字符串
    :return:
    """

    if time_string_format == "%Y" or time_string_format == "%Y-%m" or time_string_format == "%Y-%m-%d":
        timedelta = datetime.timedelta(seconds=24*60*60-1)
    else:
        timedelta = datetime.timedelta(seconds=0)

    if mode == 0:
        if start_time and end_time:
            start_time = strtodatetime(start_time, time_string_format)
            end_time = strtodatetime(end_time, time_string_format) + timedelta
        elif start_time and not end_time:
            start_time = strtodatetime(start_time, time_string_format)
            end_time = datetime.datetime.now()
        elif not start_time and end_time:
            start_time = strtodatetime("1970", "%Y")
            end_time = strtodatetime(end_time, time_string_format) + timedelta
        else:
            start_time = strtodatetime("1970", "%Y")
            end_time = datetime.datetime.now()
    else:
        raise Exception("暂不支持！")

    if compare_mode == 0:
        start_time = int(datetime2timestamp(start_time) * 1000)
        end_time = int(datetime2timestamp(end_time) * 1000)
    return start_time, end_time

# 记录日志
def logger_info_handler(logger_message):
    logger = logging.getLogger("server")
    logger.info(logger_message)