_author="niyoufa"

import sys
import math
from tornado import gen

sys.path.append("/home/nyf/develop/apidoc/server/libs")
from motorengine import Document, DateTimeField, BooleanField
from motorengine import DESCENDING

class BaseDocument(Document):
    create_time = DateTimeField(auto_now_on_insert=True)
    update_time = DateTimeField(auto_now_on_update=True)
    is_enable = BooleanField(default=True)

    @classmethod
    @gen.coroutine
    def count(cls, *args, **kwargs):
        count = yield cls.objects.filter(**kwargs).count()
        return count

    @classmethod
    @gen.coroutine
    def create(cls, *args, **kwargs):
        create_query_params = kwargs.pop("create_query_params", {})
        count = yield cls.count(**create_query_params)
        if count > 0:
            raise Exception("已存在！")
        obj = yield cls.create(**kwargs)
        return obj.to_dict()

    @classmethod
    @gen.coroutine
    def update(cls, *args, **kwargs):
        update_query_params = kwargs.pop("update_query_params", {})
        objs = yield cls.objects.filter(**update_query_params).find_all()
        for obj in objs:
            for key in kwargs:
                setattr(obj, key, kwargs.get(key))
        return [obj.to_dict() for obj in objs]

    @classmethod
    @gen.coroutine
    def get(cls, *args, **kwargs):
        if args and len(args):
            _id = args[0]
        else:
            raise Exception("param _id not found")
        obj = yield cls.objects.get(_id)
        return obj.to_dict()

    @classmethod
    @gen.coroutine
    def search(cls, page=1, page_size=10, direction=DESCENDING, field_name="create_time", **kwargs):
        objs = yield cls.objects\
            .order_by(field_name, direction=direction)\
            .skip((page-1)*page_size)\
            .limit(page_size)\
            .filter(**kwargs).find_all()
        return objs

    @classmethod
    @gen.coroutine
    def search_read(cls, page=1, page_size=10, direction=DESCENDING, field_name="create_time", **kwargs):
        objs = yield cls.search(page, page_size, direction, field_name, **kwargs)
        dict_objs = []
        for obj in objs:
            dict_objs.append(obj.to_dict())
        return dict_objs

    @classmethod
    @gen.coroutine
    def pager(cls,page=1, page_size=10, **kwargs):
        count = yield cls.count(**kwargs)
        pager = cls.count_page(count, page, page_size)
        return pager

    @classmethod
    def count_page(self, length, page, page_size=15, page_show=10):
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

    @classmethod
    @gen.coroutine
    def read(cls, ids, *args, **kwargs):
        objs = yield cls.objects.filter({"_id__in":ids}).find_all()
        return objs

    @classmethod
    @gen.coroutine
    def write(cls, ids, vals):
        objs = cls.read(ids)
        for obj in objs:
            for key in vals:
                setattr(obj, key, vals.get(key))
        return objs

    @classmethod
    def to_dict(cls):
        data = super(Document, cls).to_son()
        data['id'] = cls._id
        return data