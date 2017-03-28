#! /usr/bin/env python
# -*- coding:utf-8 -*-


import json
import tornado.web
from common import db_monitor
from tornado.escape import json_decode
import copy
import random
import sys
from formatter import convert_data
from chart import convert2piedata
import traceback
sys.path.append("../")
from common import utils


PPCITY_CONFIG_PATH = "./conf/ppcity.conf"


class PPCityHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("ppcity.html", messages=None)

    def post(self):
        req_data = json_decode(self.request.body)

        req_type = req_data.get("type", "NULL")

        if req_type == "stat":
            timeslot = req_data.get("time_slot", "NULL")

            dept_time = "NULL"
            dest_time = "NULL"

            if timeslot == "hour":
                dept_time = req_data.get("hour_start_time")
                dest_time = req_data.get("hour_start_time")
            elif timeslot == "day":
                dept_time = req_data.get("day_start_time")
                dest_time = req_data.get("day_end_time")

            resp_data = analyze_stat_data(dept_time, dest_time)

        elif req_type == "error":
            req_date = req_data.get("date", "NULL")
            stat_data = analyze_error_data(req_date)
            pie_stat_data = convert2piedata(stat_data["pie"])
            resp_data = dict()
            resp_data["pie"] = pie_stat_data
            resp_data["qid"] = stat_data["qid"]

        self.write(json.dumps(resp_data))

        return


def analyze_error_data(req_date):
    """
    0 成功
    1 验证无交通
    2 库里无酒店
    3 验证无酒店
    """
    query_sql = "select * from "

    error_dict = {
        1: "验证无交通",
        2: "库里无酒店",
        3: "验证无酒店"
    }

    stat_data = dict()
    pie_data = dict()
    error_data = dict()
    item_list = ["库里无交通", "验证无交通", "库里无酒店", "验证无酒店"]
    pie_data["item_list"] = item_list

    original_format = "%Y%m%d"
    new_format = "%Y-%m-%d"
    req_date = utils.date_formatter(req_date, original_format, new_format)
    query_sql = "select error_type, qid from verify_log where local_test = 1 and req_time like '%s%%%%';" % req_date

    try:
        query_result = db_monitor.QueryBySQL(query_sql, db_name="monitor")
    except Exception, e:
        query_result = []

    for each_query in query_result:
        qid = int(each_query.get("qid"))
        error_type = int(each_query.get("error_type"))

        if error_type == 0:
            continue

        if error_type not in error_data:
            error_data[error_type] = {"count": 1, "qid": [qid]}
        else:
            error_data[error_type]["count"] += 1
            error_data[error_type]["qid"].append(qid)

    items_data = list()
    qid_data = dict()
    for each_error, each_error_data in error_data.items():
        items_data.append({"name": error_dict[each_error],
                           "value": each_error_data["count"]})
        qid_data[error_dict[each_error]] = each_error_data["qid"]

    pie_data["items"] = items_data
    stat_data["pie"] = pie_data
    stat_data["qid"] = qid_data

    return stat_data


def analyze_stat_data(dept_time, dest_time):
    dept_time = dept_time + " 00:00:00"
    dest_time = dest_time + " 23:59:59"

    original_format = "%Y%m%d %H:%M:%S"
    new_format = "%Y-%m-%d %H:%M:%S"

    dept_time = utils.date_formatter(dept_time, original_format, new_format)
    dest_time = utils.date_formatter(dest_time, original_format, new_format)
    query_data = load_data("monitor", dept_time, dest_time)

    section_name = "PPCITY"
    new_format = "NULL"

    stat_data = convert_data(PPCITY_CONFIG_PATH, section_name, query_data,
                             flag_name=new_format)

    return stat_data


def load_data(db_name, dept_time, dest_time):
    """
    :param db_name: 数据库名称
    :param dept_time:  开始时间
    :param dest_time:  截止时间
    :return:
    """

    query_sql = "select * from verify_num where local_test != 0 and req_time > '%s' and req_time < '%s'" % (dept_time, dest_time)
    query_result = db_monitor.QueryBySQL(query_sql, db_name=db_name)

    return query_result
