_author = "niyoufa"

import pdb
from bson import ObjectId
import tornado.ioloop
from tornado import gen
import motorengine
from motorengine import Document, StringField, IntField, DateTimeField, BooleanField
from motorengine import DESCENDING

io_loop = tornado.ioloop.IOLoop.instance()
motorengine.connect("test", host="localhost", port=27017, io_loop=io_loop)

class BaseDocument(Document):
    create_time = DateTimeField(auto_now_on_insert=True)
    update_time = DateTimeField(auto_now_on_update=True)
    is_enable = BooleanField(default=True)

    def to_dict(self):libs
        data = super(Document, self).to_son()
        data['id'] = self._id
        return data

class User(BaseDocument):
    first_name = StringField(required=True)
    last_name = StringField(required=True)

class Employee(User):
    employee_id = IntField(required=True)

    @gen.coroutine
    def create(self, *args, **kwargs):
        create_query_params = kwargs.get("create_query_params") or {}
        count = yield self.count(**create_query_params)
        if count > 0:
            raise Exception("已存在！")
        first_name = kwargs.get("first_name")
        last_name = kwargs.get("last_name")
        employee_id = kwargs.get("employee_id")

        if first_name is None:
            raise Exception("用户名不能为空")

        emp = Employee(first_name=first_name, last_name=last_name, employee_id=employee_id)
        yield emp.save()
        if emp is None or emp.employee_id != employee_id:
            raise Exception("创建失败！")
        return emp

    @gen.coroutine
    def update(self, *args, **kwargs):
        emp = args[0]
        first_name = kwargs.get("first_name")
        last_name = kwargs.get("lastname")
        if first_name:
            emp.first_name = first_name
        if last_name:
            emp.last_name = last_name
        yield emp.save()
        return emp

    @gen.coroutine
    def get(self, *args, **kwargs):
        if args and len(args):
            _id = args[0]
        else:
            raise Exception("param _id not found")
        emp = yield Employee.objects.get(_id)
        return emp.to_dict()

    @gen.coroutine
    def search(self, page=1, page_size=10, direction=DESCENDING, field_name="create_time", **kwargs):
        emps = yield Employee.objects\
            .order_by(field_name, direction=direction)\
            .skip((page-1)*page_size)\
            .limit(page_size)\
            .filter(**kwargs).find_all()
        return emps

    @gen.coroutine
    def search_read(self, page=1, page_size=10, direction=DESCENDING, field_name="create_time", **kwargs):
        emps = yield self.search(page, page_size, direction, field_name, **kwargs)
        result_emps = []
        for emp in emps:
            result_emps.append(emp.to_dict())
        return result_emps

    @classmethod
    @gen.coroutine
    def count(self, *args, **kwargs):
        count = yield Employee.objects.filter(**kwargs).count()
        return count

    @gen.coroutine
    def delete(self, *args, **kwargs):
        yield Employee.objects.filter(**kwargs).delete()

    @gen.coroutine
    def bulk_insert(self, documents):
        for document in documents:
            if not type(document) == Employee:
                raise Exception("must be instance of Employee!")
        yield Employee.objects.bulk_insert(documents)

@gen.coroutine
def create_employee():
    employee_model = Employee()
    # emp = yield employee_model.create(**dict(
    #     first_name = "liudsfdasfsaydsfasfanqing",
    #     last_name = "fdsafasf",
    #     employee_id = 2011121406,
    #     create_query_params = dict(
    #         first_name = "liudsfdasfsaydsfasfanqing",
    #         employee_id = 2011121406
    #     )
    # ))
    # print(emp.first_name)
    #
    # emp = yield employee_model.update(emp, **dict(
    #     first_name = "niyoufa",
    # ))
    # print(emp.first_name)
    #
    # emp = yield employee_model.get(emp._id)
    # print(emp)
    # emps = yield employee_model.search(**dict(
    #     employee_id__in = [2011121405]
    # ))
    # for emp in emps:
    #     print(emp.employee_id)

    count = yield  employee_model.count()
    print(count)

    io_loop.stop()

io_loop.add_timeout(1, create_employee)
io_loop.start()

# __exact 精确等于 like 'aaa'
#  __iexact 精确等于 忽略大小写 ilike 'aaa'
#  __contains 包含 like '%aaa%'
#  __icontains 包含 忽略大小写 ilike '%aaa%'，但是对于sqlite来说，contains的作用效果等同于icontains。
# __gt 大于
# __gte 大于等于
# __lt 小于
# __lte 小于等于
# __in 存在于一个list范围内
# __startswith 以...开头
# __istartswith 以...开头 忽略大小写
# __endswith 以...结尾
# __iendswith 以...结尾，忽略大小写
# __range 在...范围内
# __year 日期字段的年份
# __month 日期字段的月份
# __day 日期字段的日
# __isnull=True/False

