# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
@author:Mr Bian
@licence:(C) Copyright 2018-2022. Bian Group.
@time:5/26/184:16 PM
@file:app.py
@contact:bian_wj@foxmail.com
@desc:
"""
import sys

# implement a flexible event logging system
import logging

# javascript object notation
import json

import os

# this (standard)module provides infrastructure for writing single-threaded concurrent code using coroutines
import asyncio

# module(time)
import time

# Module(datetime).class(datetime)
from datetime import datetime

# asynchronous http client/server for asyncio and python
from aiohttp import web


def main(*argv):
    # Does the basic configuration for the logging system; Then set the root logger level
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()  # create  coroutine
    loop.run_until_complete(init(loop))  # run coroutine until completed
    loop.run_forever()  # run coroutine until stop() is called


def index(request):
    # request&response are both %classes % in aiohttp.web
    return web.Response(body=b'<h1>HelloWorld</h1>')  # construct a httpresponse


# get a coroutine
@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)  # create a instance of web-server , to deal with URL/HTTP protocols
    app.router.add_route('GET', '/', index)
    # yield from   return a "coroutine of  service of monitor"
    srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server started at http://127.0.0.1:9000...')
    return srv  # srv: sockeServer


if __name__ == '__main__':
    exit(main(sys.argv[1:]))