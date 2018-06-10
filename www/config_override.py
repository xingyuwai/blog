#!/usr/bin/env python3.6
# -*- coding:utf-8 -*-

"""
@author:    Mr Bian
@license:   (C)Copyright:2018
@file:      config_override.py
@time:      18-6-9下午1:26
@desc:      
"""

import sys


def main(argv):
    """ """
    return 0


configs = {
    'db': {
        'host': '127.0.0.1'
    }
}

if __name__ == '__main__':
    exit(main(sys.argv[1:]))
