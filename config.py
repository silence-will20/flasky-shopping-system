import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config: 
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.qq.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '465'))
    #MAIL_USE_TLS = os.environ.get('MAIL_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USE_SSL = os.environ.get('MAIL_SSL', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '1830831741@qq.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'idptzbkfyzjrccde')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADED_AVATARS_DEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/static/avatars/')
    UPLOADED_STOREIMAGES_DEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/static/store_images/')
    UPLOADED_COMMODITYIMAGES_DEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/static/commodity_images/')

    @staticmethod
    def init_app(app): 
        app.config['SECRET_KEY'] = Config.SECRET_KEY
        app.config['MAIL_SERVER'] = Config.MAIL_SERVER
        app.config['MAIL_PORT'] = Config.MAIL_PORT
        #app.config['MAIL_USE_TLS'] = Config.MAIL_USE_TLS
        app.config['MAIL_USE_SSL'] = Config.MAIL_USE_SSL
        app.config['MAIL_USERNAME'] = Config.MAIL_USERNAME
        app.config['MAIL_PASSWORD'] = Config.MAIL_PASSWORD
        app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = Config.FLASKY_MAIL_SUBJECT_PREFIX
        app.config['FLASKY_MAIL_SENDER'] = Config.FLASKY_MAIL_SENDER
        app.config['FLASKY_ADMIN'] = Config.FLASKY_ADMIN
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS

class DevelopmentConfig(Config): 
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class TestingConfig(Config): 
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite://'

class ProductionConfig(Config): 
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

config = {
    'development': DevelopmentConfig, 
    'testing': TestingConfig, 
    'production': ProductionConfig, 

    'default': DevelopmentConfig
}