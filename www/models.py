#!/usr/bin/env python3.6
# -*- coding:utf-8 -*-

"""
@author:    Mr Bian
@license:   (C)Copyright:2018
@file:      models.py
@time:      18-6-7下午6:11
@desc:    models for  3 tables used in Web App
            generate sql script using Model object by script.
            e.g.: $mysql -u root -p < schema.sql  --> initialize tables of Database
"""

import sys
import time
import uuid

from .orm import Model, StringField, BooleanField, FloatField, TextField


def next_id():
    """
    in python , format output is similar to c.
    %s: string
    %d: decimal integer
    0: fill with 0
         width.precision
    %015d --> width=15, filled with 0; (without '0', filled with space)
    %s000:--> string s followed with 000
    time:
        provides time-related functions.   see also datetime & calendar module.
        time.time(): return the time in seconds(n seconds)  as a floating point number
        Universal Unique Identifier:uuid module provides immutable UUID object;
                                    uuid.uuid4() creates a random UUID.
                                    comparison of UUID objects are made by way of comparing their UUID.int
                                     which is a 128bits integer.
    """
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)


def main(argv):
    """ """

    return 0


class User(Model):
    __table__ = 'users'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    email = StringField(ddl='varchar(50)')
    passwd = StringField(ddl='varchar(50)')
    admin = BooleanField()
    name = StringField(ddl='varchar(50)')
    image = StringField(ddl='varchar(500)')
    created_at = FloatField(default=time.time)


class Blog(Model):
    __table__ = 'blogs'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    name = StringField(ddl='varchar(50)')
    summary = StringField(ddl='varchar(200)')
    content = TextField()
    created_at = FloatField(default=time.time)


class Comment(Model):
    __table__ = 'comments'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    blog_id = StringField(ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    content = TextField()
    created_at = FloatField(default=time.time)


if __name__ == '__main__':
    exit(main(sys.argv[1:]))
