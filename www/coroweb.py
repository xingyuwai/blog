#!/usr/bin/env python3.6
# -*- coding:utf-8 -*-

"""
@author:    Mr Bian
@license:   (C)Copyright:2018
@file:      coroweb.py
@time:      18-6-7下午9:15
@desc:      
"""

import sys
import asyncio
import os
import inspect
import logging
import functools
from urllib import parse  # url is a package which collects several modules working with URLs.

# third-party package
from aiohttp import web

# user defined package
from apis import APIError


def main(argv):
    """ """

    return 0


def get(path):
    """
    Define decorator @get('/path')
    then if you write codes like:
                                @get
                                def func():
                            it means func = get(path)(func)    # here get(path) is a "real " decorator.
                            thus you have a common function "func" map to a URL-handle  function.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)

        wrapper.__method__ = 'GET'
        wrapper.__route__ = path
        return wrapper

    return decorator


def post(path):
    # Define decorator @post('/path')

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)

        wrapper.__method__ = 'POST'
        wrapper.__route__ = path
        return wrapper

    return decorator



def get_required_kw_args(fn):
    """
    module inspect here is to get the infomation of parameters of function/class
                inspect.signature(fn) return a signature object for the given callable, whose value is all parameters
                                                of the callable.
                inspect.signature.parameters is object of type "mappingproxy", whose value is an "orderDICT"
                                                key   -->   parameters,  str type;
                                                value -->    @various info for the parameter @
                            parameter.kind --> type of the parameter
                                               if kind = KEYWORD_ONLY   -->the para is */*args.
                                               if kind = VAR_KEYWORD    -->the para is **kwargs.
                            parameter.default  --> return the default value of the parameter if it has;
                                                    otherwise, return class of "empty"
    :param fn:
    :return:
    """
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():    # dict.items() returns a new view of the dictionary's items((key, value))
        if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
            args.append(name)
    return tuple(args)


def get_named_kw_args(fn):
    args = []
    params = inspect.signature(fn).parameters    # signature&parameters are  classes.
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
    return tuple(args)


def has_named_kw_args(fn):
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            return True


def has_var_kw_arg(fn):
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True


def has_request_arg(fn):
    sig = inspect.signature(fn)
    params = sig.parameters
    found = False
    for name, param in params.items():
        if name == 'request':
            found = True
            continue
        if found and (
                param.kind != inspect.Parameter.VAR_POSITIONAL and param.kind != inspect.Parameter.KEYWORD_ONLY and param.kind != inspect.Parameter.VAR_KEYWORD):
            raise ValueError(
                'request parameter must be the last named parameter in function: %s%s' % (fn.__name__, str(sig)))
    return found


class RequestHandler(object):
    """
    this class encapsulate URL-handle function.
    target:
        1. analysis what parameters the URL function need;
        2. get arguments from request;
        3. call URL-function, then transform the "return" into web.Response object,
                to meet the requirement of  aiohttp frame.
    because of __call__(), instances of ReuestHandler can also be methods.

    """

    def __init__(self, app, fn):
        self._app = app
        self._func = fn
        self._has_request_arg = has_request_arg(fn)
        self._has_var_kw_arg = has_var_kw_arg(fn)
        self._has_named_kw_args = has_named_kw_args(fn)
        self._named_kw_args = get_named_kw_args(fn)
        self._required_kw_args = get_required_kw_args(fn)

    async def __call__(self, request):
        kw = None
        if self._has_var_kw_arg or self._has_named_kw_args or self._required_kw_args:
            if request.method == 'POST':
                if not request.content_type:
                    return web.HTTPBadRequest('Missing Content-Type.')
                ct = request.content_type.lower()
                if ct.startswith('application/json'):
                    params = await request.json()
                    if not isinstance(params, dict):
                        return web.HTTPBadRequest('JSON body must be object.')
                    kw = params
                elif ct.startswith('application/x-www-form-urlencoded') or ct.startswith('multipart/form-data'):
                    params = await request.post()
                    kw = dict(**params)
                else:
                    return web.HTTPBadRequest('Unsupported Content-Type: %s' % request.content_type)
            if request.method == 'GET':
                qs = request.query_string
                if qs:
                    kw = dict()
                    for k, v in parse.parse_qs(qs, True).items():
                        kw[k] = v[0]
        if kw is None:
            kw = dict(**request.match_info)
        else:
            if not self._has_var_kw_arg and self._named_kw_args:
                # remove all unamed kw:
                copy = dict()
                for name in self._named_kw_args:
                    if name in kw:
                        copy[name] = kw[name]
                kw = copy
            # check named arg:
            for k, v in request.match_info.items():
                if k in kw:
                    logging.warning('Duplicate arg name in named arg and kw args: %s' % k)
                kw[k] = v
        if self._has_request_arg:
            kw['request'] = request
        # check required kw:
        if self._required_kw_args:
            for name in self._required_kw_args:
                if not name in kw:
                    return web.HTTPBadRequest('Missing argument: %s' % name)
        logging.info('call with args: %s' % str(kw))
        try:
            r = await self._func(**kw)    # _func = fn ,call URL functions, which is a parameter of class RequestHandler
            return r
        except APIError as e:
            return dict(error=e.error, data=e.data, message=e.message)


def add_static(app):
    """
    %www/static: absolute dir into relative dir.%
    :param app:
    :return:
    """
    # abspath(path) return a normalized absolutized version of "path"
    # dirname(path): return the directory name.
    # path is absolute dir of www/static
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    """
    by router.add_static(prefix, path),   -->prefix--url prefix(start with '/');   path --- folder with files
                            redefine "prefix", to hide the real path of static resources like pic/css/js on the server,
                            or unify source files in different paths into a certain dir.
    """
    app.router.add_static('/static/', path)
    logging.info('add static %s => %s' % ('/static/', path))


def add_route(app, fn):
    """
    to register a URL-handle method
    :param app:
    :param fn:
    :return:
    """
    # getattr(object, name[,default]): a built-in method return the value of attribute "object.name";
    #  if not found--> default / AttributerError
    method = getattr(fn, '__method__', None)
    path = getattr(fn, '__route__', None)
    if path is None or method is None:
        raise ValueError('@get or @post not defined in %s.' % str(fn))

    # inspect module contains methods providing info about live objects
    # inspect.isgeneratorfunction(object) : return ture if "object" is a generator function
    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
        fn = asyncio.coroutine(fn)   # a decorator .  function_name is also a variable.
    logging.info(
        'add route %s %s => %s(%s)' % (method, path, fn.__name__, ', '.join(inspect.signature(fn).parameters.keys())))
    app.router.add_route(method, path, RequestHandler(app, fn))


def add_routes(app, module_name):
    """
    register all the functions that meet the requirement automatically in module handler
        e.g.: add_routes(app, 'handlers')
    :param app:
    :param module_name:
    :return:
    """
    # str.rfind(sub[,start[,end]]): return the highest index where substring "sub" is find in str / or str[start:end]
    # return -1 on failure.
    n = module_name.rfind('.')
    if n == (-1):
        # %__import__() equals to "import package"%
        # direct use of __import__ is discouraged in favor of  importlib.import_module(name, package=None)
        # parameter "name" specifies what module to import in absolute/relative term.
        #  ??? import_module ???
        mod = __import__(module_name, globals(), locals())
    else:
        # if "module_name" is in the form of "a.b.c.handler", get "handler".
        name = module_name[n + 1:]
        # getattr(object, name[,default]) , here mod = name of the package imported
        mod = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)
    # dir([object]) : return a list of valid attributes for the object
    for attr in dir(mod):
        # str.startswith(prefix[,start[,end]]) : return true/false
        # _var : instance var
        # __var :private var
        # __var__: exclusive var owned by python itself.
        if attr.startswith('_'):
            continue
        fn = getattr(mod, attr)   # get the value
        if callable(fn):
            method = getattr(fn, '__method__', None)
            path = getattr(fn, '__route__', None)
            if method and path:
                add_route(app, fn)


if __name__ == '__main__':
    exit(main(sys.argv[1:]))
