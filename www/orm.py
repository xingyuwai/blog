#!/usr/bin/env python3.6
# -*- coding:utf-8 -*-

"""
@author:    Mr Bian
@license:   (C)Copyright:2018
@file:      orm.py
@time:      18-6-5下午12:18
@desc:      ORM(Object Relational Mapping) is a technique  solving the mismatching between Object-Oriented &
            relational DataBase.
            @ORM has high-effeciency, but 'bad'--performance. But performance doesn't count for every system@
"""

import sys
import asyncio
import aiomysql
import logging


def main(argv):
    """ """
    return 0


def log(sql, args=()):
    logging.info('SQL:%s' % sql)  # "%s" is formatted output


@asyncio.coroutine
def create_pool(loop, **kw):
    logging.info('create database connection pool ......')
    global __pool  # connection pool saved in __pool
    # aiomysql.create_pool(minsize=1,maxsize=10) :  a coroutine that creates a pool of connections to Mysql .
    #                                               return : pool instance(class Pool)
    # port 3306 is for mysql
    __pool = yield from aiomysql.create_pool(
        host=kw.get('host', 'localhost'),
        port=kw.get('port', 3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['db'],
        # dict.get(key[,default])--> return the value for the key ; if not found, default; otherwise,None.
        # charset you want to use ,
        # e.g, 'utf8'  not utf-8 , wrong~!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        charset=kw.get('charset', 'utf8'),
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        # loop is an optional event loop instance asyncio.get_loop()is used if loop is not specified.
        loop=loop
    )


@asyncio.coroutine
def select(sql, args, size=None):
    log(sql, args)  # user defined method
    global __pool
    with (yield from __pool) as conn:  # deal with exception, with-block: do-something

        # cursor(factory=Cursor) is a method in CLASS sqlite3.Connection,
        # the parameter is a callable returning an instance of Cursor or its subclasses.
        cur = yield from conn.cursor(aiomysql.DictCursor)

        # use sql with parameters, instead of combining strings.
        # to prevent injection attack of SQL
        yield from cur.execute(sql.replace('?', '%s'), args or ())  # '?' | '%s' are placeholder for SQL | mysql
        if size:

            # if size is specified , use it; otherwise, all.
            rs = yield from cur.fetchmany(size)
        else:
            rs = yield from cur.fetchall()
        yield from cur.close()
        logging.info('rows returned : %s' % len(rs))
        return rs


@asyncio.coroutine
def execute(sql, args):
    """
    INSERT UPDATE DELETE  share this method, for they require the same parameters and
    return a integer representing the number of lines influenced
    """

    log(sql)
    with (yield from __pool) as conn:
        """
        Why use try...except... in with ... as????
        """
        try:
            cur = yield from conn.cursor()
            yield from cur.execute(sql.replace('?', '%s'), args)
            affected = cur.rowcount  # return the number of results
            yield from cur.close()

        # we can use 'e' , which is an instance of 'BaseException', to access some attribute if needed
        except BaseException as e:
            raise
    return affected


def create_args_string(num):
    L = []
    for n in range(num):
        L.append('?')
    return ','.join(L)


class Field(object):
    """  """

    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        select.default = default

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)


class StringField(Field):
    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)'):
        super().__init__(name, ddl, primary_key, default)


class BooleanField(Field):
    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', False, default)


class IntegerField(Field):

    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, 'bigint', primary_key, default)


class FloatField(Field):

    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, 'real', primary_key, default)


class TextField(Field):

    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)


class ModelMetaclass(type):
    """
    all class inheriting 'Model' can scan mapping-relationship via ModelMetaclass
    and save it into class_attrubute such as __table__ __mappings__
    """

    # the first parameter for ordinary methods:  self   , which reprents the instance itself.
    #                     for staticmethod: %omit self, i.e., none%
    #                     for classmethod:  cls.
    #                     for metaclass:     mcs.
    def __new__(mcs, name, bases, attrs):

        # exclude class 'Model' itself , %mainly for its subclasses%
        if name == 'Model':
            return type.__new__(mcs, name, bases, attrs)

        """
        'name = p1 or p2' equals to:
            if p1:
                name = p1
            else:
                name = p2.
        """
        table_name = attrs.get('__table__', None) or name
        logging.info('found model: %s (table: %s)' % (name, table_name))

        # get all Field & primary key name
        mappings = dict()
        fields = []
        primary_key = None
        for k, v in attrs.items():

            # %isinstance(value, object), whether a member of object%
            if isinstance(v, Field):
                logging.info('  found mapping: %s ==> %s' % (k, v))
                mappings[k] = v
                if v.primary_key:
                    # 找到主键:
                    if primary_key:
                        # standardError is cancelled in Python3, use Exception()
                        raise Exception('Duplicate primary key for field: %s' % k)
                    primary_key = k
                else:
                    fields.append(k)
        if not primary_key:
            raise Exception('Primary key not found.')
        for k in mappings.keys():
            attrs.pop(k)
        escaped_fields = list(map(lambda f: '`%s`' % f, fields))
        attrs['__mappings__'] = mappings  # 保存属性和列的映射关系
        attrs['__table__'] = table_name
        attrs['__primary_key__'] = primary_key  # 主键属性名
        attrs['__fields__'] = fields  # 除主键外的属性名

        # construct default of select / insert / delete
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (primary_key, ', '.join(escaped_fields), table_name)
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (
            table_name, ', '.join(escaped_fields), primary_key, create_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (
            table_name, ', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primary_key)
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (table_name, primary_key)
        return type.__new__(mcs, name, bases, attrs)


class Model(dict, metaclass=ModelMetaclass):
    """
    Model inherits dict,  with 2 special methods __getattr__() & __setattr__()
    "model" is a base-class
    """

    # P79 in <effective in python>, always use super built-in method to initialize parent classes
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:

            # the preceding "r" means --> not to escape the string
            raise AttributeError(r"'Model' object has no attribute '%s' " % key)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                # analogous to tri-operator ?:
                value = field.default() if callable(field.default) else field.default

                # str(object): return a string form for objects, for easily reading
                logging.debug('using default value for %s: %s' % (key, str(value)))
                setattr(self, key, value)
        return value

    """
    classmethods , all subclasses can call them
    e.g.:user = yield from User.find('123')
    async/wait:
        from python3.5+, we introduced "async ... await" to substitute " @asyncio.coroutine" 
        for conciseness.        
    """

    @classmethod
    async def find(cls, pk):
        # find object by primary key.
        rs = await select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])

    @classmethod
    async def find_all(cls, where=None, args=None, **kw):
        ' find objects by where clause. '
        sql = [cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args = []
        orderBy = kw.get('orderBy', None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)
        limit = kw.get('limit', None)
        if limit is not None:
            sql.append('limit')
            if isinstance(limit, int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append('?, ?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value: %s' % str(limit))
        rs = await select(' '.join(sql), args)
        return [cls(**r) for r in rs]

    @classmethod
    async def find_number(cls, selectField, where=None, args=None):
        ' find number by select and where. '
        sql = ['select %s _num_ from `%s`' % (selectField, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs = await select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']

    async def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = await execute(self.__insert__, args)
        if rows != 1:
            logging.warning('failed to insert record: affected rows: %s' % rows)

    async def update(self):
        args = list(map(self.getValue, self.__fields__))
        args.append(self.getValue(self.__primary_key__))
        rows = await execute(self.__update__, args)
        if rows != 1:
            logging.warning('failed to update by primary key: affected rows: %s' % rows)

    async def remove(self):
        args = [self.getValue(self.__primary_key__)]
        rows = await execute(self.__delete__, args)
        if rows != 1:
            logging.warning('failed to remove by primary key: affected rows: %s' % rows)


if __name__ == '__main__':
    exit(main(sys.argv[1:]))
