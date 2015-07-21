# -*-coding:utf-8 -*-
import os
import sys
import sqlite3

path = os.getcwd()
if path not in sys.path:
    sys.path.append(path)


def create_db():
    conn = sqlite3.connect('web_app.db')
    c = conn.cursor()
    c.execute('''create table users (
    id char(50) primary key not null,
    password char(50) not null,
    name char(50) unique not null)''')
    c.execute('''create table blog (
    id char(50) primary key not null,
    name char(50) not null,
    title char(50) not null,
    content text not null)''')
    conn.commit()
    conn.close()


try:
    os.mkdir(os.path.join(path, 'file'))
except FileExistsError as e:
    print(e)

try:
    create_db()
except sqlite3.OperationalError as e:
    print(e)
