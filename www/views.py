# -*-coding:utf-8 -*-
import os
import cgi
from hashlib import md5
from urllib.parse import quote, unquote

from www.models import User, Blog
from www.wsgi import render, redirect, request, Application

app = Application()


def md5_hash(value, salt=''):
    return md5((value + salt).encode()).hexdigest()


@app.route(r'/')
def login():
    if request.method == 'GET':
        return render('log_in.html')
    form = request.form
    user = User.get(name=form.get('name'))
    password = md5_hash(form.get('password', ''), salt=form.get('name', ''))
    if user is None or user.password != password:
        error = 'UserName or Password Is Incorrect'
        return render('log_in.html', error=error)
    return log_the_user_in()


def log_the_user_in():
    form = request.form
    user = User.get(name=form['name'])
    sign = md5_hash(user.id + user.password)
    app.signed_cookie[user.name] = sign
    form['sign'] = sign
    del form['password']
    request.set_cookie(form)
    return redirect('/hello')


@app.route(r'/hello')
@app.route(r'/hello/(.+)')
def hello(blog_id=None):
    name = request.cookie.get('name')
    sign = request.cookie.get('sign')
    if not sign or sign != app.signed_cookie.get(name):
        return redirect('/')

    if request.path == '/hello':
        blog = Blog.get(name=name)
        if blog is None:
            return render('hello.html', name=name)
        return redirect('/hello/' + blog.id)

    blog = Blog.get(blog_id)
    files = os.listdir(os.path.join(os.getcwd(), 'file'))
    files = ((f, quote(f).replace('%', '-')) for f in files)
    blogs = Blog.get_all(name=name)
    return render('hello.html', name=name, blog=blog, files=files, blogs=blogs)


@app.route(r'/register')
def register():
    form = request.form
    name = form.get('name')
    user = User.get(name=name)
    password = form.get('password')

    if request.method == 'GET':
        return render('register.html')
    elif user is not None:
        error = 'UserName Is Registered'
        return render('register.html', error=error)

    password = md5_hash(password, salt=name)
    user = User(name=name, password=password)
    user.insert()
    return log_the_user_in()


@app.route(r'/static/.+')
def do_with_static():
    path = os.path.join(os.getcwd(), request.path.lstrip('/'))
    mime = 'css' if path.endswith('.css') else 'javascript'
    request.header = [('Content-Type', 'text/' + mime)]
    with open(path) as f:
        request.content = f.read()
    return request


@app.route(r'/add')
def add_blog():
    name = request.cookie['name']
    return render('add_blog.html', name=name)


@app.route(r'/delete')
def delete_blog():
    Blog.delete(request.referer[-32:])
    return redirect('/hello')


@app.route(r'/update')
def update_blog():
    blog = Blog.get(id=request.referer[-32:])
    return render('update_blog.html', blog=blog)


@app.route(r'/post')
def post_blog():
    form = request.form
    if 'id' in form:
        Blog.delete(form['id'])
    blog = Blog(name=request.cookie['name'], title=form['title'],
                content=form['content'])
    blog.insert()
    return redirect('/hello/' + blog.id)


@app.route(r'/upload')
def upload():
    form = cgi.FieldStorage(fp=request.env['wsgi.input'],
                            environ=request.env,
                            keep_blank_values=True)
    item = form['file']
    if item.file and item.filename:
        filename = os.path.join(os.getcwd(), 'file', item.filename)
        with open(filename, 'wb') as f:
            for data in iter((lambda: item.file.read(1024 * 8)), b''):
                f.write(data)
    return redirect('/hello')


@app.route(r'/file/(.+)')
def download(path):
    filename = unquote(path.replace('-', '%'))
    path = os.path.join(os.getcwd(), 'file', filename)
    size = os.path.getsize(path)
    if path.endswith('resume.pdf'):
        request.header = [('Content-Type', 'application/pdf'),
                          ('Content-length', str(size)),
                          ('Content-Disposition',
                           'attachment; filename=dagger126@126.pdf')]
    else:
        request.header = [('Content-Type', 'application/x-jpg'),
                          ('Content-length', str(size)),
                          ('Content-Disposition', 'attachment;filename=xx.jpg')]
    with open(path, 'rb') as f:
        request.file = f.read()
    return request


@app.route(r'/resume')
def resume():
    return render('resume.html')


if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('', 8080, app)
    print('Serving HTTP on port 8080...')
    server.serve_forever()
