from flask import Flask
from flask import url_for,request,redirect,flash
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
app.config['SECRET_KEY']='dev'
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

@app.context_processor#模板处理上下文处理函数，该函数返回的变量将会同意注入到每一个模板上下文环境中
def inject_user():
    user=User.query.first()
    return dict(user=user)

#主页面,面对不同的请求，使用不同的返回方式
@app.route('/',methods=['GET','POST'])
def index():
    if request.method=='POST':
        #获取表单数据
        title=request.form.get('title')
        year=request.form.get('year')
        #验证数据
        if not title or not year or len(year)>4 or len(title)>60:
            flash('Invalid input.')#显示错误提示
            return redirect(url_for('index'))#重定向回主页

        #保存表单数据到数据库
        movie=Movie(title=title,year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('index'))

    user=User.query.first()
    movies=Movie.query.all()
    return render_template('index.html',user=user,movies=movies)

#编辑电影条目
@app.route('/movie/edit/<int:movie_id>',methods=['GET','POST'])
def edit(movie_id):
    movie=Movie.query.get_or_404(movie_id)

    if request.method=="POST":
        title=request.form['title']
        year=request.form['year']

        if not title or not year or len(year)>4 or len(title)>60:
            flash('Invalid input.')
            return redirect(url_for('edit',movie_id=movie_id))

        movie.title=title
        movie.year=year
        db.session.commit()
        flash('Item update.')
        return redirect(url_for('index'))
    return render_template('edit.html',movie=movie)

#删除电影条目
@app.route('/movie/delete/<int:movie_id>',methods=['POST'])
def delete(movie_id):
    movie=Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))
#创建自定义命令forge，该命令能够创建数据库
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

#异常处理
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404