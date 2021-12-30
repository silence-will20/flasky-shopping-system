from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_uploads import IMAGES, UploadSet, configure_uploads
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
avatars = UploadSet('avatars', IMAGES)
storeimages = UploadSet('storeimages', IMAGES)
commodityimages = UploadSet('commodityimages', IMAGES)
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_name): 
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    configure_uploads(app, avatars)
    configure_uploads(app, storeimages)
    configure_uploads(app, commodityimages)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .user import user as user_blueprint
    app.register_blueprint(user_blueprint, url_prefix='/user')

    from .store import store as store_blueprint
    app.register_blueprint(store_blueprint, url_prefix='/store')

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    return app