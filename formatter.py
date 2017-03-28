#! /usr/bin/env python
# -*- coding:utf-8 -*-

import ConfigParser
import traceback
import json
import sys
import operator
sys.path.append("../")
from chart import convert2linedata
from common import error_code
from common.utils import date_formatter


OPERATOR_DICT = {
    ">=": operator.gt,
    "<=": operator.lt,
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    "<": operator.le
    }


def parse_configure(config_path, section_name):
    """
    解析配置文件
    """
    config_data = dict()

    config = ConfigParser.ConfigParser()
    try:
        config.read(config_path)
    except Exception, e:
        traceback.print_exc(e)
        return error_code.CONFIG_NOT_EXIST, config_data

    try:
        stat_name = config.get(section_name, "name")
        config_data["name"] = stat_name

        chart_type = config.get(section_name, "chart")
        chart_type = chart_type.upper()
        if chart_type not in ("LINE", "PIE"):
            print "config :: chart type must be LINE or PIE"
            return error_code.CONFIG_PARSE_ERROR, config_data
        else:
            config_data["chart"] = chart_type
    except Exception, e:
        traceback.print_exc(e)
        return error_code.CONFIG_PARSE_ERROR, config_data

    if chart_type == "LINE":
        try:
            y_max = config.get(section_name, "y_max")
            y_max = int(y_max)
            config_data["y_max"] = y_max
        except:
            config_data["y_max"] = 120

        try:
            y_min = config.get(section_name, "y_min")
            y_min = int(y_min)
            config_data["y_min"] = y_min
        except:
            config_data["y_min"] = 0

        try:
            label_format = config.get(section_name, "label_format")
            label_item = config.get(section_name, "label_item")
            config_data["label_format"] = label_format
            config_data["label_item"] = label_item
        except Exception, e:
            traceback.print_exc(e)
            return error_code.CONFIG_PARSE_ERROR, config_data

    try:
        item_list_str = config.get(section_name, "item_list")
        item_list = item_list_str.split("|")
        if not item_list:
            print "config :: No items in item_list section"
            return error_code.CONFIG_PARSE_ERROR, config_data

        items_data = dict()
        for each_item in item_list:
            item_name = config.get(each_item, "name")
            value = config.get(each_item, "value")

            if chart_type == "PIE":
                try:
                    req_count = config.get(each_item, "req_count")
                    success_count = config.get(each_item, "success_count")
                except:
                    req_count = "NULL"
                    success_count = "NULL"
            else:
                req_count = config.get(each_item, "req_count")
                success_count = config.get(each_item, "success_count")

            items_data[each_item] = {"name": item_name,
                                     "req_count": req_count,
                                     "success_count": success_count,
                                     "value": value}
        config_data["items"] = items_data
    except Exception, e:
        traceback.print_exc(e)
        return error_code.CONFIG_PARSE_ERROR, config_data

    return error_code.RUN_OK, config_data


def parse_operator(stat_item_str):
    """
    解析给定统计条件中的运算符号
    输入参数是表示整个条件的字符串
    输出结果是包含要统计的项目名称，判断的运算符号以及比较的值
    """

    operators = OPERATOR_DICT.keys()
    operate_items = ["", ""]

    temp_stat_list = stat_item_str.split("|")
    count_flag, real_stat_item_str = temp_stat_list

    for each_op in operators:
        if each_op in real_stat_item_str:
            operate_items = real_stat_item_str.split(each_op)
            break

    return operate_items[0], operate_items[1], OPERATOR_DICT[each_op], count_flag


def convert2chartdata(query_data, config_data, flag_name):
    """
    将从数据库中 select 出来的数据，按照配置文件的规则，转换成绘图需要的格式
    """
    stat_data = dict()
    chart_type = config_data.get("chart", "NULL")
    if chart_type == "NULL":
        print "config :: wrong chart type parsed"
        return stat_data

    chart_name = config_data.get("name", "")
    if chart_type == "LINE":
        stat_data = convert_line_data(query_data, config_data, flag_name)
    elif chart_type == "PIE":
        stat_data = convert_pie_data(query_data, config_data)

    return stat_data


def convert_pie_data(query_data, config_data):
    pass


def convert_line_data(query_data, config_data, flag_name):
    """
    将 query 得到的数据，按照配置文件要求的格式，转化成折线图所需要的数据格式
    """
    original_stat_data = stat_line_data(query_data, config_data, flag_name)

    y_max = config_data.get("y_max")
    y_min = config_data.get("y_min")
    original_stat_data["y_max"] = y_max
    original_stat_data["y_min"] = y_min

    title_name = config_data.get("name", "NULL")
    if title_name != "NULL":
        original_stat_data["title_name"] = title_name

    new_stat_data = convert2linedata(original_stat_data)

    return new_stat_data


def stat_line_data(query_data, config_data, flag_name):
    """
    对于折线图所需要的数据，第一步得到的数据格式如下:
    stat_data = {stat_item:
                    {
                        x_label:
                            {
                                name: xxx,
                                req_count: xxx,
                                success_count: xxx,
                                value: xxx,
                            }
                    }
                }

    然后将 stat_item 拿出来排序得到要统计的项目；
    将所有的 x_label 拿出来得到排序得到 x 轴坐标；
    """
    stat_data = dict()
    config_items = config_data.get("items", {})
    if not config_items:
        print "config :: no config data parsed"
        return stat_data

    label_data = dict()
    label_data["name"] = config_data.get("label_item")
    label_data["format"] = config_data.get("label_format")

    for each_item, each_item_data in config_items.items():
        each_item_stat_data = get_item_stat(each_item, each_item_data,
                                            label_data, flag_name, query_data)
        stat_data[each_item] = each_item_stat_data

    all_x_labels = list()
    for each_item, each_stat_data in stat_data.items():
        for each_label in each_stat_data.keys():
            if each_label not in all_x_labels:
                all_x_labels.append(each_label)
    all_x_labels.sort()

    new_stat_data = dict()
    new_stat_data["label"] = all_x_labels

    item_list = stat_data.keys()
    item_list.sort()
    new_item_list = list()

    items_data = dict()
    for each_item in item_list:
        each_item_list = list()
        each_item_name = config_data["items"][each_item].get("name")
        new_item_list.append(each_item_name)
        for each_label in all_x_labels:
            stat_info = stat_data[each_item].get(each_label, {})
            if not stat_info:
                if config_data["items"][each_item].get("value") == "RATE":
                    each_item_list.append({"name": each_item_name,
                                           "success": 0, "count": 0,
                                           "value": 100})
            else:
                if config_data["items"][each_item].get("value") == "RATE":

                    if stat_info.get("req_count") != stat_info.get("success_count"):
                        each_item_value = float(stat_info["success_count"]) / \
                            stat_info["req_count"] * 100
                    else:
                        each_item_value = 100
                elif config_date["items"][each_item].get("value") == "COUNT":
                    each_item_value = int(stat_info.get("success_count", 0))

                each_rate_dict = {
                    "name": each_item_name,
                    "count": int(stat_info["req_count"]),
                    "success": int(stat_info["success_count"]),
                    "value": each_item_value
                }
                each_item_list.append(each_rate_dict)

        items_data[each_item_name] = each_item_list

    new_stat_data["item_list"] = new_item_list
    new_stat_data["items"] = items_data

    return new_stat_data


def get_label(original_label, label_format, flag_name):
    """
    解析 x 轴，目前遇见的有按照天/小时统计两种情况，
    目前的格式为: TIME##%Y%m%d %H:%M:%S|FLAG##%Y%m%d
    用竖线分隔原始时间格式和转换之后的时间格式
    如果 flag_name 不为 NULL，则使用 flag_name 代替转换后的时间格式
    """
    real_label = ""
    original_label = str(original_label)
    if label_format.startswith("TIME"):
        label_format_list = label_format.split("|")

        original_format = label_format_list[0].split("##")[1]

        if flag_name == "NULL":
            flag_format = label_format_list[1].split("##")[1]
        else:
            flag_format = flag_name

        real_label = date_formatter(original_label, original_format,
                                    flag_format)

    return real_label


def get_item_stat(each_item, items_data, label_data, flag_name, query_data):
    """
    计算每一个统计项目的数据
    """
    each_item_data = dict()

    label_key = label_data.get("name")
    label_format = label_data.get("format")

    item_name = items_data.get("name")
    item_req_count_rule = items_data.get("req_count")
    item_suc_count_rule = items_data.get("success_count")

    req_key, req_compare_value, req_op, count_flag = parse_operator(item_req_count_rule)
    succ_key, succ_compare_value, succ_op, count_flag = parse_operator(item_suc_count_rule)

    req_count = 0
    success_count = 0
    for each_query in query_data:
        label_value = each_query.get(label_key)
        real_label = get_label(label_value, label_format, flag_name)

        if count_flag == "COUNT":
            if req_op(str(each_query.get(req_key)), req_compare_value):
                if real_label not in each_item_data:
                    each_item_data[real_label] = {
                        "req_count": 1,
                        "success_count": 0
                    }
                else:
                    each_item_data[real_label]["req_count"] += 1
            else:
                continue

            if succ_op(str(each_query.get(succ_key)), succ_compare_value):
                each_item_data[real_label]["success_count"] += 1
        elif count_flag == "VALUE":
            if real_label not in each_item_data:
                each_item_data[real_label] = {
                    "req_count": int(each_query.get(req_key)),
                    "success_count": int(each_query.get(succ_key))
                }


    return each_item_data


def convert_data(config_path, section_name, query_data, flag_name="NULL"):
    """
    输入配置文件地址，section name 和 query data，按照流程转化为画图需要的数据
    """
    stat_data = dict()
    _error, config_data = parse_configure(config_path, section_name)

    if _error != error_code.RUN_OK:
        print "config :: parse configure file failure."
        return error_code.CONFIG_PARSE_ERROR, stat_data

    stat_data = convert2chartdata(query_data, config_data, flag_name)

    return stat_data


if __name__ == "__main__":
    config_path = "./conf/ppscore.conf"
    section_name = "ALL"
    query_data = list()
    convert_data(config_path, section_name, query_data)
