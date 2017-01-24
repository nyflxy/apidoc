_author="niyoufa"

import pdb

from bson import ObjectId
import tornado
from tornado import gen
from tornado.web import HTTPError

from server.handler import BaseHandler

from addons.apidoc.models import Modular

# 接口模块
class ModularsHandler(BaseHandler):

    @tornado.web.asynchronous
    @gen.coroutine
    def get(self, *args, **kwargs):
        # 获取所有接口模块列表
        modulars = yield Modular.objects.find_all()
        self.write_json([modular.to_dict() for modular in modulars])

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self, *args, **kwargs):
        self.modular_id = self.get_argument("modular_id")
        self.name = self.get_argument("name")
        self.description = self.get_argument("description", "")
        self.owner = self.get_argument("owner")
        modular = yield Modular.objects.get(modular_id = self.modular_id)
        if modular:
            self.write_json({}, status_code=1, msg="已存在！")
            return

        modular = Modular(modular_id=self.modular_id, name=self.name, description=self.description, owner=self.owner)
        yield modular.save()

        modular = modular.to_dict()
        self.write_json(modular, status_code=0, msg="添加成功")

    @tornado.web.asynchronous
    @gen.coroutine
    def delete(self, *args, **kwargs):
        self.modular_id = self.get_argument("modular_id")
        yield Modular.objects.delete()
        self.write_json({}, status_code=0, msg="删除成功")



