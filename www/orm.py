#!/usr/bin/env python3.6
# -*- coding:utf-8 -*-

"""
@author:    Mr Bian
@license:   (C)Copyright:2018
@file:      orm.py
@time:      18-6-5下午12:18
@desc:      
"""

import sys
import asyncio
import aiomysql
import logging


def main(argv):
    """ """
    return 0


def log(sql, args=()):
    logging.info('SQL:%s' % sql)


if __name__ == '__main__':
    exit(main(sys.argv[1:]))
