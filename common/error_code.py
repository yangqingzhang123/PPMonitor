#! /usr/bin/env python
# -*- coding:utf-8 -*-

RUN_OK = 0
CONFIG_NOT_EXIST = 10
SECTION_MISSED = 11
CONFIG_PARSE_ERROR = 12

ERROR_CODE = {
    0: "正确",
    10: "配置文件不存在",
    11: "缺少对应的 section",
    12: "解析错误",
}
