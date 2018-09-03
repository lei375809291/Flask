from flask import Blueprint,jsonify
from flask_login import current_user


posts = Blueprint('posts', __name__)


@posts.route('/publish/')
def publish():
    return '发表博客'


# 接受并处理ajax请求
@posts.route('/collect/<int:pid>/')
def collect(pid):
    #判断是否已经收藏
    if current_user.is_favorite(pid):
        current_user.del_favorite(pid)
        status='收藏'
    else:
        current_user.add_favorite(pid)
        status='取消收藏'
    return jsonify({'status':status})
