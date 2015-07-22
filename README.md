# webApp
A simple web framework for fun

一个微型的web框架, 实现了基本的ORM, MVC

数据库使用python内置的sqlite3, 前端页面使用jinja2模板引擎+bootstrap生成

服务器端使用nginx+uwsgi

视图中实现了一个简单的博客系统

实现了用户的注册,登录,以及博客的增加,更新,删除, 图片的上传,下载功能

增加了rebuild分支, 使用flask风格重构了大部分代码

使用实例对象代替了类对象实现wsgi接口

使用装饰器生成url路由

使用namedtuple属性对象传递sqlite3游标对象从而替代全局变量

重构后,代码耦合度降低,业务逻辑书写更加简便
