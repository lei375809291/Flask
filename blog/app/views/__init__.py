from .main import main
from .user import user
from .posts import posts



DEFAULT_BLUEPRINT=(
    # 蓝本加前缀
    (main, ''),
    (user, '/user'),
    (posts, '/posts')
)

def register_blueprint(app):
    for blueprint,url_prefix in DEFAULT_BLUEPRINT:
        app.register_blueprint(blueprint,url_prefix=url_prefix)