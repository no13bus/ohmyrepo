# coding: UTF-8
import asyncio
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.autoreload
from tornado.options import define, options
from handlers import *
import session
from settings import settings
from cache import RedisCacheBackend
import redis

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=True, help="debug mode", type=bool)
define("mongo_host", default="127.0.0.1:27017", help="database host")

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/logout", LogoutHandler),
            (r"/webhook", WebhookHandler),
            (r"/callback", CallbackHandler),
            (r"/stars", UserStarHandler),
            (r"/follows", UserFollowingHandler),
            (r"/cities", UserCityhandler),
            (r"/f", FollowHandler),
            (r"/uf", UnfollowHandler),
            (r"/add", AddWebhookHandler),
            (r"/show", ShowHandler),
            (r"/login", LoginHandler),
            (r"/howitworks", HowHandler),
            (r"/stat", StatHandler),
            (r"/users", StatUserHandler),
            (r"/repos", StatRepoHandler),
            (r"/export", ExportHandler),

        ]
        self.session_manager = session.TornadoSessionManager(settings["session_secret"], settings["session_dir"])
        self.redis = redis.Redis()
        self.cache = RedisCacheBackend(self.redis)
        debug = False
        tornado.web.Application.__init__(self, handlers, **settings)


# async def main():
#     tornado.options.parse_command_line()
#     application = tornado.web.Application([(r"/", MainHandler)])
#     http_server = tornado.httpserver.HTTPServer(application)
#     http_server.listen(options.port)
#     await asyncio.Event().wait()


async def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
