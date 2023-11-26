from flask import Flask
from flask import url_for
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
import os
import sys
import click

#实例化一个app网页
app=Flask(__name__)

#定义不同系统下的数据库路径
WIN=sys.platform.startswith('win')
if WIN:
    prefix='sqlite:///'
else:
    prefix='sqlite:////'

app.config['SQLALCHEMY_DATABASE_URI']=prefix+os.path.join(app.root_path,'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False #关闭对模型修改的监控

#实例一个数据库
db=SQLAlchemy(app)

#创建数据库模型
class User(db.Model):#表名将会是user
    id=db.Column(db.Integer,primary_key=True)#主键
    name=db.Column(db.String(20))#名字

class Movie(db.Model):#表名将会是movie
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(60))#电影标题
    year=db.Column(db.String(4))#电影年份

#自定义数据库初始化命令
@app.cli.command()
@click.option('--drop',is_flag=True,help='Create after drop.')
    #设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')#输出提示信息

@app.route('/')
def index():
    user=User.query.first()
    movies=Movie.query.all()
    return render_template('index.html',user=user,movies=movies)

@app.route('/user/<user>')
def user_page(user):
    return 'User: %s'% user

#创建自定义命令forge
@app.cli.command()
def forge():
    """generate fake data"""
    db.create_all()
    # 定义虚拟数据
    name = 'Dave Sum'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]

    user=User(name=name)
    db.session.add(user)
    for m in movies:
        movie=Movie(title=m['title'],year=m['year'])
        db.session.add(movie)

    db.session.commit()
    click.echo('Done.')
