#! /usr/bin/env python
# -*- coding:utf-8 -*-

import time
import datetime
from datetime import datetime


def date_formatter(original_date, original_format, new_format):
    """
    日期格式化函数，将传入的日期转换成新的日期格式
    """

    date_obj = datetime.strptime(original_date, original_format)

    return date_obj.strftime(new_format)
