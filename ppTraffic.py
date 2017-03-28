#! /usr/bin/env python
# -*- coding:utf-8 -*-


import json
import tornado.web
from common import db_monitor
from tornado.escape import json_decode
import copy
import random
import sys
from chart import convert2linedata
from chart import convert2piedata
import traceback
sys.path.append("../")
from common import utils


class PPTrafficHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("ppcity.html", messages=None)

    def post(self):
        req_data = json_decode(self.request.body)
        resp_data = dict()

        self.write(json.dumps(resp_data))

        return
