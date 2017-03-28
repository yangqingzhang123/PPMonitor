#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
    Created on 2014-03-08
    @author: devin
    @desc:
        数据访问
"""

import MySQLdb
from MySQLdb.cursors import DictCursor
# from util.logger import logger

# MySQL 连接信息
MYSQL_HOST = '10.10.151.68'
MYSQL_PORT = 3306
MYSQL_USER = 'reader'
MYSQL_PWD = 'miaoji1109'


def GetConnection(db_name='monitor'):
    conn = MySQLdb.connect(host=MYSQL_HOST, user=MYSQL_USER, passwd=MYSQL_PWD,
                           db=db_name, charset="utf8")
    return conn


def ExecuteSQL(sql, args=None, db_name='base_data'):
    """
        执行SQL语句, 正常执行返回影响的行数，出错返回Flase
    """
    try:
        conn = GetConnection(db_name)
        cur = conn.cursor()
        ret = cur.execute(sql, args)
        conn.commit()
    except MySQLdb.Error, e:
        # logger.error("ExecuteSQL error: %s" %str(e))
        print str(e)
        return False
    finally:
        cur.close()
        conn.close()

    return ret


def ExecuteSQLs(sql, args=None, db_name='monitor'):
    """
        执行多条SQL语句, 正常执行返回影响的行数，出错返回Flase
    """
    try:
        conn = GetConnection(db_name)
        cur = conn.cursor()

        ret = cur.executemany(sql, args)
        conn.commit()
    except MySQLdb.Error, e:
        # logger.error("ExecuteSQL error: %s" %str(e))
        print str(e)
        return False
    finally:
        cur.close()
        conn.close()

    return ret


def QueryBySQL(sql, args=None, db_name='monitor'):
    """
        通过sql查询数据库，正常返回查询结果，否则返回None
    """
    results = []
    try:
        print sql
        conn = GetConnection(db_name)
        cur = conn.cursor(cursorclass=DictCursor)

        cur.execute(sql, args)
        rs = cur.fetchall()
        for row in rs:
            results.append(row)
    except MySQLdb.Error, e:
        # logger.error("QueryBySQL error: %s" %str(e))
        print str(e)
        return None
    finally:
        cur.close()
        conn.close()

    return results
