from flask import Blueprint, render_template, flash, redirect, url_for, current_app, request,session
from app.forms import RegisterForm, LoginForm, UploadForm,PasswordForm,EmailForm,Reset_pw_Form,Chongzhi_pw_Form
from app.email import send_mail
from app.models import User
from app.extensions import db, photos
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from flask_login import login_user, logout_user, login_required, current_user
import os
from PIL import Image


user=Blueprint('user',__name__)

# 用户注册
@user.route('/register/',methods=['GET','POST'])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        u=User(username=form.username.data,
               password=form.password.data,
               email=form.email.data)
        db.session.add(u)
        db.session.commit()
        s=Serializer(current_app.config['SECRET_KEY'],expires_in=3600)
        token=s.dumps({'id':u.id})
        send_mail('账户激活',
                  form.email.data,
                  'email/activate.html',
                  username=form.username.data,
                  token=token)
        flash('注册成功，请点击邮件中的链接完成激活')
        return redirect(url_for('main.index'))
    return render_template('user/register.html',form=form)

# 用户激活
@user.route('/activate/<token>')
def activate(token):
    s=Serializer(current_app.config['SECRET_KEY'])
    try:
        data=s.loads(token)
    except:
        flash('激活失败')
        return redirect(url_for('main.index'))

    # 根据token中携带的用户信息，在数据库中查询用户
    u = User.query.get(data['id'])
    # 判断是否激活
    if not u.confirmed:
        # 没有激活才需要激活
        u.confirmed = True
        # 再次保存修改
        db.session.add(u)
    flash('激活成功')
    return redirect(url_for('user.login'))

# 用户登录
@user.route('/login/',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        u=User.query.filter(User.username==form.username.data).first()
        if not u:
            flash('无效用户名')
        elif not u.confirmed:
            flash('账户未激活')
        elif not u.verify_password(form.password.data):
            flash('密码无效')
        else:
            flash('登陆成功')
            # 退出浏览器保留登录信息
            from datetime import timedelta
            login_user(u,remember=True,duration=timedelta(hours=3) )
            return redirect(request.args.get('next')or url_for('main.index'))
    return render_template('user/login.html',form=form)

# 用户退出
@user.route('/logout/')
def logout():
    flash('您已退出登录')
    logout_user()
    return redirect(url_for('main.index'))

@user.route('/profile/')
# 保护路由，该路由必须登录才能访问
@login_required
def profile():
    return render_template('user/profile.html')

# 上传图片

@user.route('/icon/', methods=['GET', 'POST'])
def icon():
    form = UploadForm()
    if form.validate_on_submit():
        # 提取上传文件信息
        photo = form.photo.data
        # 提取文件后缀
        suffix = os.path.splitext(photo.filename)[1]
        # 生成随机文件名
        filename = random_string() + suffix
        # 保存上传文件
        photos.save(photo, name=filename)
        # 拼接文件路径名
        pathname = os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], filename)
        # 打开文件
        img = Image.open(pathname)
        # 设置尺寸
        img.thumbnail((64, 64))
        # 重新保存
        img.save(pathname)
        # 删除原来的头像文件（默认头像除外）
        if current_user.icon != 'default.jpg':
            os.remove(os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], current_user.icon))
        # 保存头像
        current_user.icon = filename
        db.session.add(current_user)
        flash('头像修改成功')
    img_url = url_for('static', filename='upload/'+current_user.icon)
    return render_template('user/icon.html', form=form, img_url=img_url)


def random_string(length=32):
    from random import choice
    base_str = 'abcdefghijklmnopqrstuvwxyz1234567890'
    return ''.join(choice(base_str) for i in range(length))

# 修改密码
@user.route('/changepw/', methods=['GET', 'POST'])
@login_required
def changepw():
    form=PasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password1.data):
            current_user.password = form.password2.data
            db.session.add(current_user)
            flash('密码修改成功')
        else:
            flash('原密码错误')
    return render_template('user/changepw.html', form=form)
# 修改邮箱
@user.route('/change_em/',methods=['GET','POST'])
@login_required
def change_em():
    flash('请谨慎填写邮箱修改地址，如果邮箱地址不正确，将导致账号无法登陆')
    form=EmailForm()
    if form.validate_on_submit():
        current_user.email=form.newemail.data
        current_user.confirmed=False
        db.session.add(current_user)
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=3600)
        token = s.dumps({'id': current_user.id})
        # 发送用户激活邮件
        send_mail('账户激活',
                  form.newemail.data,
                  'email/activate.html',
                  username=current_user,
                  token=token)
        # 弹出消息提示用户下一步操作
        flash('注册成功，请点击邮件中的链接完成激活')
        return render_template('user/change_em.html',form=form)
# 忘记密码
@user.route('/reset_pw/',methods=['GET','POST'])
def reset_pw():
    form=Reset_pw_Form()
    if form.validate_on_submit():
        u = User.query.filter(User.username == form.username.data).first()
        if not u:
            flash('用户名不存在')
            return render_template('user/reset_pw.html', form=form)
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=3600)
        token = s.dumps({'id': u.id})
        send_mail('密码重置',
                  u.email,
                  'email/reset_password.html',
                  username=form.username.data,
                  token=token)
        flash('密码重置邮件发送成功，请点击邮件中的链接完成密码重置')
    return render_template('user/reset_pw.html',form=form)
# 重置密码
@user.route('/chongzhi_pw/<token>',methods=['GET','POST'])
def chongzhi_pw(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    form = Chongzhi_pw_Form()
    try:
        data = s.loads(token)
    except:
        flash('验证失败')
        return redirect(url_for('main.index'))
    u = User.query.get(data['id'])
    if form.validate_on_submit():
        u.password = form.password.data
        db.session.add(u)
        flash('密码重置成功')
    return render_template('user/chongzhi_pw.html',form=form)


# 博客收藏页面
# @user.route('/collection/')
# def collection():
#     return render_template('user/collection.html')