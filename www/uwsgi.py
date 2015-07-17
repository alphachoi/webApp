# -*-coding:utf-8 -*-
import sys

path = '/webApp'
if path not in sys.path:
    sys.path.append(path)

from www.wsgi import Application as application
