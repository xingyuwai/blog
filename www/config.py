#!/usr/bin/env python3.6
# -*- coding:utf-8 -*-

"""
@author:    Mr Bian
@license:   (C)Copyright:2018
@file:      config.py
@time:      18-6-9下午1:27
@desc:      config_default.py -->  development
            config_override.py --> product
            read config_override.py in priority.
"""

import sys

from config_default import configs


def main(argv):
    """ """

    return 0


class Dict(dict):
    '''
    ??? Simple dict but support access as x.y style. ???
    '''

    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value


def merge(defaults, override):

    r = {}
    for k, v in defaults.items():
        if k in override:
            if isinstance(v, dict):
                r[k] = merge(v, override[k])
            else:
                r[k] = override[k]
        else:
            r[k] = v
    return r


def to_dict(d):
    """
    transform a dict into  Dict which supports access like x.y .
    :param d:
    :return:
    """
    D = Dict()
    for k, v in d.items():
        D[k] = to_dict(v) if isinstance(v, dict) else v
    return D


try:
    import config_override

    configs = merge(configs, config_override.configs)
except ImportError:
    pass

configs = to_dict(configs)

if __name__ == '__main__':
    exit(main(sys.argv[1:]))
