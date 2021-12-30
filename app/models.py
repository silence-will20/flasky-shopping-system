from sqlalchemy.orm import backref, defaultload
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime

class Role(db.Model): 
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None: 
            self.permissions = 0

    def add_permission(self, perm): 
        if not self.has_permission(perm): 
            self.permissions += perm
    
    def remove_permission(self, perm): 
        if self.has_permission(perm): 
            self.permissions -= perm
    
    def reset_permissions(self): 
        self.permissions = 0

    def has_permission(self, perm): 
        return self.permissions & perm == perm

    def __repr__(self): 
        return '<role %r>' % self.name

    @staticmethod
    def insert_roles(): 
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.PURCHASE], 
            'Store': [Permission.FOLLOW, Permission.COMMENT, Permission.SALE, Permission.MANAGE_COMMODITY], 
            'Administrator': [Permission.FOLLOW, Permission.COMMENT, Permission.PURCHASE, Permission.ADMIN]
        }
        default_role = 'User'
        for r in roles: 
            role = Role.query.filter_by(name=r).first()
            if role is None: 
                role = Role(name = r)
            role.reset_permissions()
            for perm in roles[r]: 
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

class Permission: 
    FOLLOW = 1
    COMMENT = 2
    SALE = 4
    PURCHASE = 8
    MANAGE_COMMODITY = 16
    ADMIN = 32

class User(UserMixin, db.Model): 
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email= db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index = True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar = db.Column(db.String(64), default='default/default_avatar.jpg')
    addresses = db.relationship('Address', backref='user')
    basket = db.relationship('Basket', backref='user')
    order = db.relationship('Order', backref='user', cascade='all, delete-orphan')
    store = db.relationship('Store', backref='user', cascade='all, delete-orphan')

    def __init__(self, **kwargs): 
        super(User, self).__init__(**kwargs)
        if self.role is None: 
            if self.email == current_app.config['FLASKY_ADMIN']: 
                self.role = Role.query.filter_by(name='Administrator').first()
                self.role_id = self.role.id
            if self.role is None: 
                self.role = Role.query.filter_by(default=True).first()
                self.role_id = self.role.id


    def __repr__(self): 
        return '<user %r>' % self.username

    def can (self, perm): 
        return self.role is not None and self.role.has_permission(perm)
    
    def is_administrator(self): 
        return self.can(Permission.ADMIN)
    
    def is_store(self): 
        return self.can(Permission.SALE)

    @property
    def password(self): 
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password): 
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password): 
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600): 
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token): 
        s = Serializer(current_app.config['SECRET_KEY'])
        try: 
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id: 
            return False
        self.confirmed = True
        db.session.add(self)
        return True

class AnonymousUser(AnonymousUserMixin): 
    def can(self, permissions): 
        return False
    def is_administrator(self): 
        return False

from . import login_manager

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def login_user(user_id): 
    return User.query.get(int(user_id))

class Address(db.Model): 
    __tablename__ = 'addresses'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    address = db.Column(db.String(128))
    phone = db.Column(db.String(64))
    real_name = db.Column(db.String(64))

class Commodity_category(db.Model): 
    __tablename__ = 'commodity_categories'
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(64))
    commodities = db.relationship('Commodity', backref='commodity_category', cascade='all, delete-orphan')

    def __repr__(self): 
        return '<Commodity_category %r>' % self.category_name

    @staticmethod
    def insert_commodity_categories(): 
        commmodity_categories = [
            '服装 & 饰品', 
            '母婴用品', 
            '美容', 
            '电子产品', 
            '家具', 
            '家居 & 园艺', 
            '箱包', 
            '鞋', 
            '体育 & 娱乐', 
            '手表'
        ]
        for c in commmodity_categories: 
            commodity_category = Commodity_category.query.filter_by(category_name=c).first()
            if commodity_category is None: 
                commodity_category = Commodity_category(category_name = c)
            db.session.add(commodity_category)
        db.session.commit()

class Store(db.Model): 
    __tablename__ = 'stores'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    storename = db.Column(db.String(64), unique=True, index=True)
    storeaddress = db.Column(db.String(128))
    real_name = db.Column(db.String(64))
    storeimage = db.Column(db.String(64))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    about_store = db.Column(db.String(128))
    commodities = db.relationship('Commodity', backref='store', cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='store', cascade='all, delete-orphan')

class Commodity(db.Model): 
    __tablename__ = 'commodities'
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
    commodity_category_id = db.Column(db.Integer, db.ForeignKey('commodity_categories.id'))
    inventory = db.Column(db.Integer)
    price = db.Column(db.Float)
    about_commodity = db.Column(db.String(128))
    sales_volume = db.Column(db.Integer, default=0)
    commodityname = db.Column(db.String(64))
    commodityimage = db.Column(db.String(64))
    orders = db.relationship('Order', backref='commodity', cascade='all, delete-orphan')
    baskets = db.relationship('Basket', backref='commodity', cascade='all, delete-orphan')

class Basket(db.Model): 
    __tablename__ = 'baskets'
    id = db.Column(db.Integer, primary_key=True)
    commodity_id = db.Column(db.Integer, db.ForeignKey('commodities.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    number = db.Column(db.Integer)

class Payment(db.Model): 
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    paymentname = db.Column(db.String(64))
    orders = db.relationship('Order', backref='payment', cascade='all, delete-orphan')
    
    @staticmethod
    def insert_payments(): 
        paymentnames = [
            '微信支付', 
            '支付宝支付'
        ]
        for paymentname in paymentnames: 
            payment = Payment.query.filter_by(paymentname=paymentname).first()
            if payment is None: 
                payment = Payment(paymentname = paymentname)
            db.session.add(payment)
        db.session.commit()

class Order(db.Model): 
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
    time = db.Column(db.DateTime, default=datetime.utcnow)
    commodity_id = db.Column(db.Integer, db.ForeignKey('commodities.id'))
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'))
    address = db.Column(db.String(128))
    number = db.Column(db.Integer)
    price = db.Column(db.Float)