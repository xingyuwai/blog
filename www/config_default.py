#!/usr/bin/env python3.6
# -*- coding:utf-8 -*-

"""
@author:    Mr Bian
@license:   (C)Copyright:2018
@file:      config_default.py
@time:      18-6-9下午1:26
@desc:      configure file for DEVELOPMENT,
            username/password etc. of database
            A web application need to read a configuration file
            different config files needed in different environment
"""

import sys


def main(argv):
    """ """

    return 0


configs = {
    'debug': True,
    'db': {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'www',
        'password': 'www',
        'db': 'awesome'
    },
    'session': {
        'secret': 'Awesome'
    }
}

if __name__ == '__main__':
    exit(main(sys.argv[1:]))
