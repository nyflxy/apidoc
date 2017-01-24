_author="niyoufa"

from tornado.options import options

from server.handler import APINotFoundHandler

from addons.apidoc.handlers import ModularsHandler


urls = [
    [r'/api/apidoc/modulars', ModularsHandler],
    [r'.*', APINotFoundHandler],
]

# Add subpath to urls
for u in urls:
    u[0] = options.subpath + u[0]

