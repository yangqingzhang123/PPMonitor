#! /usr/bin/env python
# -*- coding:utf-8 -*-

import copy


ITEM_LIST = [
    {
        "name": '邮件营销',
        "type": 'line',
        "data": [120, 132, 101, 134, 90, 230, 210]
    },
    {
        "name": '联盟广告',
        "type": 'line',
        "data": [220, 182, 191, 234, 290, 330, 310]
    },
    {
        "name": '视频广告',
        "type": 'line',
        "data": [150, 232, 201, 154, 190, 330, 410]
    },
    {
        "name": '直接访问',
        "type": 'line',
        "data": [320, 332, 301, 334, 390, 330, 320]
    },
    {
        "name": '搜索引擎',
        "type": 'line',
        "data": [820, 932, 901, 934, 1290, 1330, 1320]
    }
]


def convert2linedata(stat_data):
    """
    将统计数据转化为折线图需要的数据
    :param stat_data:
    :return:
    """

    data = {
        "title": {
            "text": ''
        },

        "tooltip": {
            "trigger": 'axis',
            "hideDelay": 5,
        },

        "legend": {
            "data": []  # 项目名称列表
        },

        "plotOptions": {
            "series": {
                "stickyTracking": False
            }
        },

        "xAxis": [
            {
                "type": 'category',
                "boundaryGap": False,
                "name": "时刻",
                "data": []  # 横座标列表
            }
        ],
        "yAxis": [
            {
                "type": 'value',
                "boundaryGap": [0, 10],
                "max": 120,
                "min": 0,
                "name": "成功率",
                "axisLabel": {
                    "formatter": "{value} %"
                }
            }
        ],
        "series": [
        ]
    }

    title_name = stat_data.get("name", "NULL")
    if title_name != "NULL":
        data["title"]["text"] = title_name

    x_labels = stat_data.get("label")
    data["xAxis"][0]["data"] = x_labels

    y_max = stat_data.get("y_max", -1)
    if y_max != -1:
        data["yAxis"][0]["max"] = y_max

    y_min = stat_data.get("y_min", -1)
    if y_min != -1:
        data["yAxis"][0]["min"] = y_min

    items_data = stat_data.get("items")

    item_list = stat_data.get("item_list")
    data["legend"]["data"] = item_list
    for idx, each_item in enumerate(item_list):
        stat_item = copy.deepcopy(ITEM_LIST[idx])
        stat_item["name"] = each_item
        stat_item["data"] = items_data[each_item]
        data["series"].append(stat_item)

    return data


def convert2piedata(stat_data):

    data = {
        "title": {
            "text": "",
            "subtext": "",
            "x": "center"
            },

        "tooltip": {
            "trigger": "item",
            "formatter": "{a} <br/>{b} : {c} ({d}%)"
            },

        "legend": {
            "orient": "vertical",
            "left": "left",
            "data": ["直接访问", "邮件营销", "联盟广告", "视频广告", "搜索引擎"]
            },

        "series": [{
            "name": "类型",
            "type": "pie",
            "radius": "75%",
            "data":[
                {"value": 335, "name": "直接访问"},
                {"value": 310, "name": "邮件营销"},
                {"value": 234, "name": "联盟广告"},
                {"value": 135, "name": "视频广告"},
                {"value": 1548, "name": "搜索引擎"}
                ],
            "itemStyle": {
                "emphasis": {
                    "shadowBlur": 10,
                    "shadowOffsetX": 0,
                    "shadowColor": "rgba(0, 0, 0, 0.5)"
                }
            }
        }]
    }

    title_name = stat_data.get("name", "NULL")
    if title_name != "NULL":
        data["title"]["text"] = title_name

    sub_title_name = stat_data.get("sub_name", "NULL")
    if sub_title_name != "NULL":
        data["title"]["subtext"] = sub_title_name

    item_list = stat_data.get("item_list")
    data["legend"]["data"] = item_list

    items_data = stat_data.get("items")
    data["series"][0]["data"] = items_data

    return data
