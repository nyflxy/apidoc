_author="niyoufa"

import pdb
import json
import datetime
import math
from tornado.options import options
import pymongo
from bson.json_util import dumps
from bson.objectid import ObjectId

mongo_client = pymongo.MongoClient(options.MONGODB_HOST, options.MONGODB_PORT)

def singleton(cls, *args, **kw):
    instances = {}
    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton

class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance

class BaseModel(object):

    def __init__(self, name):
        self.name = name

    def create(self,vals,*args,**kwargs):
        """
        在数据库中插入一条记录
        :param vals: 待新建记录的字段值，字典类型
        :return:新建记录的id
        """
        raise Exception("不能实例化！")

    def search(self,page,page_size,*args,**kwargs):
        """
        查询符合条件的记录
        :param args: 包含检索条件的tuples列表 可用的操作：=,<,>,<=,>=,in,like,ilike,child_of
        :param page:分页索引
        :param page_size:分页大小
        :param context:分页大小
        :return:符合条件记录的id_list
        """
        raise Exception("不能实例化！")

    def read(self,ids,fields=None,*args,**kwargs):
        """
        返回记录的指定字段值列表
        :param ids:待读取的记录的id列表
        :param fields:待读取的字段值,默认读取所有字段
        :return:返回读取结果的字典列表
        """
        raise Exception("不能实例化！")

    def browse(self,select,page,page_size,*args,**kwargs):
        """
        浏览对象及其关联对象
        :param select: 待返回的对象id或id列表
        :param page:
        :param page_size:
        :return:返回对象或对象列表
        """
        raise Exception("不能实例化！")

    def write(self,ids,vals,*args,**kwargs):
        """
        保存一个或几个记录的一个或几个字段
        :param ids:待修改的记录的id列表
        :param vals:待保存的字段新值，字典类型
        :return:如果没有异常，返回True，否则抛出异常
        """
        raise Exception("不能实例化！")

    def unlink(self,ids,*args,**kwargs):
        """
        删除一条或几条记录
        :param ids:待删除记录的id列表
        :return:如果没有异常，返回True，否则抛出异常
        """
        raise Exception("不能实例化！")

    # 计算分页信息
    def count_page(self,length, page, page_size=15, page_show=10):
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
            "total": length,
        }
        return pager

    # 打印
    def dump(self,obj):
        result = None
        if isinstance(obj, pymongo.cursor.Cursor) or \
                isinstance(obj, list) or \
                isinstance(obj, pymongo.command_cursor.CommandCursor):
            result = []
            for _s in obj:
                if type(_s) == type({}):
                    s = {}
                    for (k, v) in _s.items():
                        if type(v) == type(ObjectId()):
                            s[k] = json.loads(dumps(v))['$oid']
                        elif type(v) == type(datetime.datetime.utcnow()):
                            s[k] = v.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        else:
                            s[k] = v
                else:
                    s = _s
                result.append(s)
        elif isinstance(obj, dict):
            for (k, v) in obj.items():
                if type(v) == type(ObjectId()):
                    obj[k] = json.loads(dumps(v))['$oid']
                elif type(v) == type(datetime.datetime.utcnow()):
                    obj[k] = v.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            result = obj
        elif isinstance(obj, pymongo.results.InsertOneResult):
            result = {"inserted_id": str(obj.inserted_id)}
        elif obj is None:
            result = None
        elif len(obj) == 0:
            result = obj
        return result

    # 生成objectid
    def create_objectid(self,str=None):
        try:
            object_id = ObjectId(str)
        except:
            object_id = ''
        return object_id

class MongoDB(BaseModel):

    def __init__(self, name):
        self.name = name
        self.coll = self.get_coll()
        self.columns = self.get_columns()

    def coll_name(self):
        return self.name.split(".")[1]

    def db_name(self):
        return self.name.split(".")[0]

    def get_coll(self):
        db_name = self.name.split(".")[0]
        coll_name = self.name.split(".")[1]
        db = mongo_client[db_name]
        coll = db[coll_name]
        return coll

    def get_columns(self):
        if self.coll.find().count() > 0:
            document = self.coll.find_one()
            columns = document.keys()
        else:
            columns = []
        return columns

    def get_count(self,query_params):
        query_params.update(
            is_enable=True,
        )
        count = self.coll.find(query_params).count()
        return count

    def create(self,vals,*args,**kwargs):
        curr_time = datetime.datetime.now()
        vals["create_date"] = str(curr_time)
        vals["write_date"] = str(curr_time)
        vals["is_enable"] = True
        self.coll.insert_one(vals)
        return {"id":str(vals["_id"])}

    def search(self,page=1,page_size=10,*args,**kwargs):
        # 查询参数
        query_params = kwargs.get("query_params") or {}
        query_params.update(dict(
            is_enable=True,
        ))

        # 排序参数
        sort_params = kwargs.get("sort_params") or {}
        if sort_params == {}:
            sort_params.update({"create_date": -1})

        pager_flag = kwargs.get("pager_flag") or True # 是否分页

        if pager_flag:
            length = self.coll.find(query_params).count()
            pager = self.count_page(length, page, page_size)
            cr = self.coll.aggregate([
                {"$match": query_params},
                {"$sort": sort_params},
                {"$skip": pager['skip']},
                {"$limit": pager['page_size']}])
        else:
            pager = self.count_page(0, 0, 0)
            cr = self.coll.aggregate([
                {"$match": query_params},
                {"$sort": sort_params}])

        ids = []
        for obj in cr:
            obj = self.dump(obj)
            ids.append(obj.get("_id"))

        return ids, pager

    def read(self,ids,fields=None,*args,**kwargs):
        query_params = {}
        query_params.update(dict(
            is_enable=True,
        ))

        objectids = []
        for _id in ids:
            id = self.create_objectid(_id)
            objectids.append(id)
        query_params.update({
            "_id":{"$in":objectids}
        })

        cr = self.coll.aggregate([
            {"$match": query_params}])
        objs = []
        for obj in cr:
            obj = self.dump(obj)
            objs.append(obj)
        return objs

    def search_read(self,page=1,page_size=10,*args,**kwargs):
        # 查询参数
        query_params = kwargs.get("query_params") or {}
        query_params.update(dict(
            is_enable=True,
        ))

        # 排序参数
        sort_params = kwargs.get("sort_params") or {}
        if sort_params == {}:
            sort_params.update({"create_date": -1})

        pager_flag = kwargs.get("pager_flag") or True  # 是否分页

        if pager_flag:
            length = self.coll.find(query_params).count()
            pager = self.count_page(length, page, page_size)
            cr = self.coll.aggregate([
                {"$match": query_params},
                {"$sort": sort_params},
                {"$skip": pager['skip']},
                {"$limit": pager['page_size']}])
        else:
            pager = self.count_page(0, page, page_size)
            cr = self.coll.aggregate([
                {"$match": query_params},
                {"$sort": sort_params}])

        objs = []
        for obj in cr:
            obj = self.dump(obj)
            objs.append(obj)
        return objs, pager

    def write(self,vals,ids=[],*args,**kwargs):
        query_params = {}
        query_params.update(dict(
            is_enable=True,
        ))

        objectids = []
        for _id in ids:
            id = self.create_objectid(_id)
            objectids.append(id)
        query_params.update({
            "_id": {"$in": objectids}
        })

        cr = self.coll.find(query_params)
        curr_date = datetime.datetime.now()
        vals.update(dict(
            write_date = curr_date,
        ))
        for obj in cr:
            obj.update(vals)
            self.coll.save(obj)

    def update(self,vals,*args,**kwargs):
        query_params = kwargs.get("query_params") or {}
        query_params.update(dict(
            is_enable=True,
        ))
        cr = self.coll.find(query_params)
        curr_date = datetime.datetime.now()
        vals.update(dict(
            write_date=curr_date,
        ))
        for obj in cr:
            obj.update(vals)
            self.coll.save(obj)

    def unlink(self,ids,*args,**kwargs):
        query_params = kwargs.get("query_params") or {}
        query_params.update(dict(
            is_enable=True,
        ))

        objectids = []
        for _id in ids:
            id = self.create_objectid(_id)
            objectids.append(id)

        query_params.update({
            "_id":{"$in":objectids}
        })

        cr = self.coll.find(query_params)
        curr_date = datetime.datetime.now()
        for obj in cr:
            obj.update({"write_date":curr_date,"is_enable":False})
            self.coll.save(obj)

    def search_unlink(self,*args, **kwargs):
        query_params = kwargs.get("query_params") or {}
        query_params.update(dict(
            is_enable=True,
        ))
        cr = self.coll.find(query_params)
        curr_date = datetime.datetime.now()
        for obj in cr:
            obj.update({"write_date": curr_date, "is_enable": False})
            self.coll.save(obj)