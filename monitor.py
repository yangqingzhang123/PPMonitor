#! /usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import tornado.auth
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import os.path
import uuid
import json
import pprint
import urllib
from tornado.escape import json_decode
from tornado.escape import json_encode
import requests
import time
import datetime
import re
from common import db_monitor
from ppScore import PPScoreHandler
from ppCity import PPCityHandler
from ppView import PPViewHandler
from ppTraffic import PPTrafficHandler

from tornado.options import define, options

define("port", default=8900, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/ppscore", PPScoreHandler),
            (r"/ppcity", PPCityHandler),
            (r"/ppview", PPViewHandler),
            (r"/pptraffic", PPTrafficHandler)
        ]
        settings = dict(
            debug=True,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static")
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class PPTrafficHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("pptraffic.html", messages=None)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", messages=None)


def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
