#! /usr/bin/env python
# -*- coding:utf-8 -*-

import json
import tornado.web
from common import db_monitor
from tornado.escape import json_decode
import copy
import random
from formatter import convert_data


# define const variable
PPSCORE_CONFIG_PATH = "./conf/ppscore.conf"


class PPScoreHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("ppscore.html", messages=None)

    def post(self):
        req_data = json_decode(self.request.body)

        timeslot = req_data.get("time_slot", 1)
        api_type = req_data.get("api_type")

        dept_time = "NULL"
        dest_time = "NULL"

        if timeslot == "hour":
            dept_time = req_data.get("hour_start_time")
            dest_time = req_data.get("hour_start_time")
        elif timeslot == "day":
            dept_time = req_data.get("day_start_time")
            dest_time = req_data.get("day_end_time")

        query_data = load_data("monitor", api_type, dept_time, dest_time)
        resp_data = stat_data(api_type, query_data, timeslot)

        self.write(json.dumps(resp_data))

        return


def stat_data(api_type, query_data, stat_type):
    stat_data = dict()

    section_name = ""
    if api_type == "all":
        section_name = "ALL"
    elif api_type == "csv010":
        section_name = "REQ_CSV010"
    elif api_type == "csv011":
        section_name = "REQ_CSV011"
    elif api_type == "csv012":
        section_name = "REQ_CSV012"

    if stat_type == "hour":
        new_format = "%H"
    else:
        new_format = "NULL"

    stat_data = convert_data(PPSCORE_CONFIG_PATH, section_name, query_data,
                             flag_name=new_format)

    return stat_data


def load_data(db_name, api_type, dept_time, dest_time):
    """
    :param api_type: API 请求类型
    :param dept_time:  开始时间
    :param dest_time:  截止时间
    :return:
    """

    if api_type == "all":
        query_sql = "SELECT * FROM `ppscore_monitor` WHERE req_time > '%s 00:00:00' AND req_time < '%s 23:59:59'" % (
            dept_time, dest_time)
    else:
        query_sql = "SELECT * FROM `ppscore_monitor` WHERE rq_type = '%s' AND req_time > '%s 00:00:00' AND req_time < '%s 23:59:59'" % (
            api_type, dept_time, dest_time)

    query_result = db_monitor.QueryBySQL(query_sql, db_name=db_name)

    return query_result
