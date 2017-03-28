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


intensity_dict = {0: '轻松', 1: '适中', 2: '紧张', 3: '不够'}


def load_error_dict():
    """
    从数据库中 load ppview 项目的错误代码对应关系
    """

    sql = "select * from ppview_error_reason;"
    result = db_monitor.QueryBySQL(sql, db_name="ppview")

    error_dict = dict()
    for each_error in result:
        error_dict[int(each_error["error_id"])] = each_error["error_reason"]

    return error_dict


error_dict = load_error_dict()


class PPViewHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("ppview.html", messages=None)

    def post(self):
        req_data = json_decode(self.request.body)

        req_type = req_data.get("type", "NULL")
        resp_data = dict()

        if req_type == "stat":
            stat_start_time = req_data.get("stat_start_time", "NULL")
            stat_end_time = req_data.get("stat_end_time", "NULL")
            env_name = req_data.get("env_name", "NULL")
            stat_data = analyze_stat_data(stat_start_time, stat_end_time,
                                          env_name)
            resp_data = convert2linedata(stat_data)
        elif req_type == "kpi":
            kpi_time = req_data.get("kpi_time", "NULL")
            stat_data = analyze_kpi_data(kpi_time)
            resp_data = convert2linedata(stat_data)

        elif req_type == "kpi_info":
            req_date = req_data.get("date", "NULL")
            kpi_stat_data = stat_kpi_info(req_date)

            resp_data = dict()
            for each_type, each_kpi_info in kpi_stat_data.items():
                each_kpi_stat_data = convert2piedata(each_kpi_info)
                resp_data[each_type] = each_kpi_stat_data

        elif req_type == "error":
            stat_date = req_data.get("date", "NULL")
            env_name = req_data.get("env", "NULL")
            error_stat_info = stat_error_info(stat_date, env_name)

            resp_data = dict()
            for each_type, each_error_info in error_stat_info.items():
                resp_data[each_type] = convert2piedata(each_error_info)

        self.write(json.dumps(resp_data))

        return


def stat_kpi_info(req_date):
    """
    统计 KPI 相关指标
    """
    stat_data = dict()

    query_sql = "select type, error_id, poiThrow, widgetStats, hasTimeOut from ppview_kpi_log where type = 'ssv005' and date = '%s'" % req_date
    try:
        result = db_monitor.QueryBySQL(query_sql, db_name="ppview")
    except:
        return stat_dict

    # 失败原因统计
    error_rate_info = dict()
    error_rate_stat_data = dict()
    for each_data in result:
        try:
            error_id = int(each_data.get("error_id", "NULL"))
            req_type = each_data.get("type", "NULL")
        except Exception, e:
            print str(e)
            continue

        if error_id == 0:
            continue

        req_key = "_".join([req_type, str(error_id), error_dict.get(int(error_id), "NULL")])
        if req_key not in error_rate_stat_data:
            error_rate_stat_data[req_key] = 1
        else:
            error_rate_stat_data[req_key] += 1

    item_list = error_rate_stat_data.keys()
    item_list.sort()
    error_rate_info["item_list"] = item_list

    items_data = list()
    for each_item in item_list:
        items_data.append({"name": each_item,
                           "value": error_rate_stat_data.get(each_item, 0)})
    error_rate_info["items"] = items_data
    error_rate_info["name"] = "错误占比统计"
    error_rate_info["sub_name"] = "总数 : %d" % sum(error_rate_stat_data.values())

    # 最优规划统计
    best_plan_info = dict()
    best_plan_stat_data = dict()
    for each_data in result:
        try:
            error_id = int(each_data.get("error_id", "NULL"))
            time_out_flag = each_data.get("hasTimeOut", "NULL")
        except:
            continue

        if error_id != 0:
            continue

        if time_out_flag == "false":
            req_key = "最优规划"
        else:
            req_key = "非最优规划"

        if req_key not in best_plan_stat_data:
            best_plan_stat_data[req_key] = 1
        else:
            best_plan_stat_data[req_key] += 1

    item_list = best_plan_stat_data.keys()
    best_plan_info["item_list"] = item_list

    items_data = list()
    for each_item in item_list:
        items_data.append({"name": each_item,
                           "value": best_plan_stat_data.get(each_item, 0)})
    best_plan_info["items"] = items_data
    best_plan_info["name"] = "最优规划统计"
    best_plan_info["sub_name"] = "总数 : %d" % sum(best_plan_stat_data.values())

    # 丢点统计
    thrown_point_info = dict()
    thrown_point_stat_data = dict()

    for each_data in result:
        try:
            poi_throw = int(each_data.get("poiThrow"))
            widget_status = int(each_data.get("widgetStats"))
        except:
            continue

        if poi_throw <= 0:
            continue

        req_key = intensity_dict.get(widget_status, -1)
        if req_key not in thrown_point_stat_data:
            thrown_point_stat_data[req_key] = 1
        else:
            thrown_point_stat_data[req_key] += 1

    item_list = thrown_point_stat_data.keys()
    item_list.sort()
    thrown_point_info["item_list"] = item_list

    items_data = list()
    for each_item in item_list:
        items_data.append({"name": each_item,
                           "value": thrown_point_stat_data.get(each_item, 0)})
    thrown_point_info["items"] = items_data
    thrown_point_info["name"] = "丢点统计"
    thrown_point_info["sub_name"] = "总数 : %d" % sum(thrown_point_stat_data.values())

    stat_data["error"] = error_rate_info
    stat_data["best"] = best_plan_info
    stat_data["thrown"] = thrown_point_info
    return stat_data


def analyze_kpi_data(kpi_time):
    """
    0 成功
    1 验证无交通
    2 库里无酒店
    3 验证无酒店
    """

    stat_data = dict()

    query_sql = "select * from ppview_kpi_summary where type = 'ssv005' and date like '%s%%%%';" % kpi_time
    try:
        query_result = db_monitor.QueryBySQL(query_sql, db_name="ppview")
    except Exception, e:
        return stat_data

    item_list = ["成功率"]
    stat_data["item_list"] = item_list
    stat_data["name"] = "PPView KPI 统计"
    stat_data["y_max"] = 105
    stat_data["y_min"] = 90

    kpi_stat_data = dict()
    for each_query in query_result:
        try:
            req_date = each_query.get("date")
            error_id = each_query.get("error_id")
            error_count = int(each_query.get("error_num"))
            if req_date not in kpi_stat_data:
                if error_id == "0":
                    kpi_stat_data[req_date] = {"req_count": error_count,
                                               "success_count": error_count}
                else:
                    kpi_stat_data[req_date] = {"req_count": error_count,
                                               "success_count": 0}
            else:
                if error_id == "0":
                    kpi_stat_data[req_date]["req_count"] += error_count
                    kpi_stat_data[req_date]["success_count"] += error_count
                else:
                    kpi_stat_data[req_date]["req_count"] += error_count
        except Exception, e:
            continue

    x_labels = kpi_stat_data.keys()
    x_labels.sort()
    stat_data["label"] = x_labels

    items_data = dict()
    for each_item in item_list:
        each_item_list = list()

        for each_label in x_labels:
            stat_info = kpi_stat_data.get(each_label, {})
            if not stat_info:
                each_item_list.append({"name": each_item, "count": 0, "value": 100, "success": 0})
            else:
                if each_item == "成功率":
                    each_item_rate = float(stat_info["success_count"]) / stat_info["req_count"] * 100
                    success_count = int(stat_info["success_count"])

                each_rate_dict = {
                    "name": each_item,
                    "count": int(stat_info["req_count"]),
                    "success": success_count,
                    "value": each_item_rate,
                }
                each_item_list.append(each_rate_dict)

        items_data[each_item] = each_item_list

    stat_data["items"] = items_data

    return stat_data


def analyze_stat_data(stat_start_time, stat_end_time, env_name):
    query_data = load_stat_data("ppview", stat_start_time, stat_end_time,
                                env_name)

    req_stat_data = dict()
    for each_query_data in query_data:
        each_stat_day = each_query_data.get("date")
        success_flag = int(not bool(int(each_query_data.get("error_id"))))

        if each_stat_day not in req_stat_data:
            req_stat_data[each_stat_day] = {"req_count": 1,
                                            "success_count": success_flag}
        else:
            req_stat_data[each_stat_day]["req_count"] += 1
            req_stat_data[each_stat_day]["success_count"] += success_flag

    new_stat_data = dict()
    all_x_labels = req_stat_data.keys()
    all_x_labels.sort()

    item_list = ["成功率"]
    new_stat_data["label"] = all_x_labels
    new_stat_data["item_list"] = item_list

    items_data = dict()
    for each_item in item_list:
        each_item_list = list()

        for each_label in all_x_labels:
            stat_info = req_stat_data.get(each_label, {})

            if not stat_info:
                each_item_list.append({"name": each_item, "count": 0,
                                      "value": 100, "success": 0})
            else:
                if each_item == "成功率":
                    req_count = int(stat_info.get("req_count"))
                    success_count = int(stat_info.get("success_count"))

                if (success_count == req_count):
                    each_item_rate = 100
                else:
                    each_item_rate = float(success_count) / req_count * 100

                each_rate_dict = {
                    "name": each_item,
                    "count": req_count,
                    "success": success_count,
                    "value": each_item_rate,
                    "env": env_name
                }
                each_item_list.append(each_rate_dict)

        items_data[each_item] = each_item_list

    new_stat_data["items"] = items_data
    new_stat_data["name"] = "PPView 统计"
    new_stat_data["y_max"] = 105
    new_stat_data["y_min"] = 90

    return new_stat_data


def stat_error_info(stat_date, env_name):
    """
    统计成功、失败、超时有结果、超时无结果的比例
    """
    stat_data = dict()
    error_data = load_error_data(stat_date, env_name)

    # 统计正确率占比
    success_rate_info = dict()
    success_rate_stat_data = dict()
    for each_data in error_data:
        try:
            req_type = each_data.get("type", "NULL")
            error_id = int(each_data.get("error_id", "NULL"))
        except:
            continue

        if error_id != 0:
            continue

        if req_type not in success_rate_stat_data:
            success_rate_stat_data[req_type] = 1
        else:
            success_rate_stat_data[req_type] += 1

    item_list = success_rate_stat_data.keys()
    item_list.sort()
    success_rate_info["item_list"] = item_list
    items_data = list()
    for each_item in item_list:
        items_data.append({"name": each_item,
                           "value": success_rate_stat_data[each_item]})
    success_rate_info["items"] = items_data
    success_rate_info["name"] = "正确占比统计"
    success_rate_info["sub_name"] = "总数 : %s" % str(sum(success_rate_stat_data.values()))

    # 错误占比统计
    error_rate_info = dict()
    error_rate_stat_data = dict()
    for each_data in error_data:
        try:
            req_type = each_data.get("type", "NULL")
            error_id = int(each_data.get("error_id", "NULL"))
        except:
            continue

        if error_id == 0:
            continue

        req_key = "_".join([req_type, error_dict.get(int(error_id), "NULL")])
        if req_key not in error_rate_stat_data:
            error_rate_stat_data[req_key] = 1
        else:
            error_rate_stat_data[req_key] += 1

    item_list = error_rate_stat_data.keys()
    item_list.sort()
    error_rate_info["item_list"] = item_list

    items_data = list()
    for each_item in item_list:
        items_data.append({"name": each_item,
                           "value": error_rate_stat_data.get(each_item, 0)})
    error_rate_info["items"] = items_data
    error_rate_info["name"] = "错误占比统计"
    error_rate_info["sub_name"] = "总数 : %s" % str(sum(error_rate_stat_data.values()))

    # ssv005 占比统计
    ssv005_rate_info = dict()
    ssv005_rate_stat_data = dict()
    for each_data in error_data:
        try:
            req_type = each_data.get("type", "NULL")
            error_id = int(each_data.get("error_id", "NULL"))
            time_out_flag = each_data.get("hasTimeOut", "NULL")
        except:
            continue

        if req_type != "ssv005":
            continue

        req_key = "_".join([error_dict.get(error_id), time_out_flag]).encode("utf-8")
        req_key = req_key.replace("true", "超时").replace("false", "未超时")
        if req_key not in ssv005_rate_stat_data:
            ssv005_rate_stat_data[req_key] = 1
        else:
            ssv005_rate_stat_data[req_key] += 1

    item_list = ssv005_rate_stat_data.keys()
    item_list.sort()
    ssv005_rate_info["item_list"] = item_list

    items_data = list()
    for each_item in item_list:
        items_data.append({"name": each_item,
                           "value": ssv005_rate_stat_data.get(each_item, 0)})
    ssv005_rate_info["items"] = items_data
    ssv005_rate_info["name"] = "SSV005 统计"
    ssv005_rate_info["sub_name"] = "总数 : %s" % str(sum(ssv005_rate_stat_data.values()))

    stat_data["success"] = success_rate_info
    stat_data["error"] = error_rate_info
    stat_data["ssv005"] = ssv005_rate_info
    return stat_data


def load_error_data(stat_date, env_name):
    """
    根据统计日期和开发环境名称，load 错误的数据
    """
    sql = "select * from ppview_chat_%s_log where date = '%s';" % (env_name,
                                                                   stat_date)
    result = db_monitor.QueryBySQL(sql, db_name="ppview")

    return result


def load_stat_data(db_name, stat_start_time, stat_end_time, env_name):
    """
    :param db_name: 数据库名称
    :param stat_time:  需要统计的日期
    :param env_name: 测试环境/正式环境
    :return:
    """

    if stat_start_time != stat_end_time:
        query_sql = "select error_id, date from ppview_chat_%s_log where date >= '%s' and date <= '%s'" % (
            env_name, stat_start_time, stat_end_time)
    else:
        query_sql = "select error_id, date from ppview_chat_%s_log where date = '%s'" % (
            env_name, stat_start_time)

    query_result = db_monitor.QueryBySQL(query_sql, db_name=db_name)

    return query_result
