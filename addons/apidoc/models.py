_author="niyoufa"

from motorengine import StringField, UUIDField, IntField, BooleanField, URLField, ListField, JsonField, \
                        ReferenceField

from server.model import BaseDocument

# 接口模块
class Modular(BaseDocument):
    modular_id = StringField(required=True)
    name = StringField(required=True)
    description = StringField(default="")
    owner = StringField(required=True)
    order = ListField(base_field=StringField(), default=[])
    folders = ListField(base_field=JsonField(),default=[])
    timestamp = IntField(default=0)
    public = BooleanField(default=False)
    requests = ListField(base_field=JsonField(),default=[])

# # 接口子模块
# class Folder(BaseDocument):
#     collectionId = ReferenceField(reference_document_type=Modular)
#     folder_id = UUIDField(required=True)
#     name = StringField(required=True)
#     description = StringField(default="")
#     owner = StringField(required=True)
#     order = ListField(base_field=StringField(), default=[])
#
# # 接口
# class Request(BaseDocument):
#     collectionId = ReferenceField(reference_document_type=Modular)
#     request_id = UUIDField(required=True)
#     name = StringField(required=True)
#     url = URLField(required=True)
#     method = StringField(required=True)
#     description = StringField(default="")
#     headers = StringField(default="")
#     preRequestScript = JsonField(default={})
#     pathVariables = JsonField(default={})
#     data = ListField(base_field=JsonField(),default=[])
#     dataMode = StringField(default="")
#     tests = ListField(base_field=JsonField(), default=[])
#     currentHelper = StringField()
#     helperAttributes = JsonField(default={})
#     time = IntField()
#     responses = ListField(base_field=JsonField(),default=[])


