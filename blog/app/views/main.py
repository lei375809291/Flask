from flask import Blueprint, render_template, current_app, flash, redirect, url_for,request
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import PostsForm
from app.models import Posts
from app.extensions import db
from flask_login import current_user


# 创建蓝本
main=Blueprint('main',__name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostsForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('登录后才可发表')
            return redirect(url_for('user.login'))
        u = current_user._get_current_object()
        p = Posts(content=form.content.data, user=u)
        db.session.add(p)
        flash('发表成功')
        return redirect(url_for('main.index'))
    # 读取所有发表博客的数据（不分页）
    # posts= Posts.query.filter(Posts.rid==0).order_by(Posts.timestamp.desc()).all()
    # 分页查询发表博客的数据
    # 获取当前页码
    page=request.args.get('page',1,int)
    pagination=Posts.query.filter(Posts.rid==0).order_by(Posts.timestamp.desc()).paginate(page=page,per_page=10,error_out=False)
    posts=pagination.items
    return render_template('main/index.html', form=form,posts=posts,pagination=pagination)

# 生成token
@main.route('/generate/')
def generate():
    s=Serializer(current_app.config['SECRET_KEY'],expires_in=3600)
    token=s.dumps({'id':666})
    return token

@main.route('/check/<token>/')
def check(token):
    s=Serializer(current_app.config['SECRET_KEY'])
    data = s.loads(token)
    return str(data['id'])

@main.route('/jiami/')
def jiami():
    return generate_password_hash('534534')


@main.route('/jiaoyan/<password>/')
def jiaoyan(password):
    if check_password_hash('pbkdf2:sha256:50000$xAM8nq56$55b89980ef6f9c866aadab54f39c2dd98910d35b88ac3f220a5b422582a923a2', password):
        return '密码正确'
    return '密码错误'