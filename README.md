## webApp

一个微型的web框架, 实现了基本的ORM, MVC, [项目入口](http://umaru.net/)

数据库使用python内置的sqlite3, 前端页面为jinja2模板引擎+bootstrap生成

服务器端采用nginx+uwsgi

视图中完成了一个简单的博客系统

实现了用户的注册,登录,以及博客的增加,更新,删除, 图片的上传,下载功能

增加了rebuild分支, 采用flask风格重构了大部分代码

改用实例对象代替类对象实现了wsgi接口

使用装饰器生成url路由

优化了数据库连接, 使用全局对象减少了数据库连接花费

重构后,代码耦合度降低,业务逻辑书写更加简便

另外使用django和flask重写了业务逻辑

###参考资料

* ORM部分: http://www.liaoxuefeng.com/ python教程实战部分的ORM实现

* wsgi接口: http://anandology.com/blog/how-to-write-a-web-framework-in-python/

* url路由: flask源码
