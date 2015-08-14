# -*-coding:utf-8 -*-
import os
import sys
import sqlite3

path = os.getcwd()
if path not in sys.path:
    sys.path.append(path)

try:
    os.mkdir(os.path.join(path, 'file'))
except FileExistsError as e:
    print(e)


def get_db_connection():
    conn = sqlite3.connect('web_app.db')
    conn.row_factory = sqlite3.Row
    with conn:
        try:
            conn.execute('''create table users (
            id char(50) primary key not null,
            password char(50) not null,
            name char(50) unique not null)''')
            conn.execute('''create table blog (
            id char(50) primary key not null,
            name char(50) not null,
            title char(50) not null,
            content text not null)''')
        except sqlite3.OperationalError as error:
            print(error)
    return conn
