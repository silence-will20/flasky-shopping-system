from flask.helpers import flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.core import BooleanField, FloatField, IntegerField, SelectField
from wtforms.fields.simple import FileField
from wtforms.validators import DataRequired, Email, Length, Regexp, ValidationError
from ..models import Commodity_category, Role, Store, User
from app import avatars

class EditProfileAdminForm(FlaskForm): 
    email = StringField('用户邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('用户昵称', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, '用户名只能包含字母、数字、.和下划线')])
    confirmed = BooleanField('confirmed')
    role = SelectField('Role', coerce=int)

    def __init__(self, user, *args, **kwargs): 
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field): 
        if field.data != self.user.email and User.query.filter_by(email=field.data).first(): 
            raise ValidationError('该邮箱已被注册！')
    
    def validate_username(self, field): 
        if field.data != self.user.username and User.query.filter_by(username=field.data).first(): 
            raise ValidationError('该用户名已被他人使用！')

class EditUserProfileAdminForm(FlaskForm): 
    email = StringField('用户邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('提交')

class EditStoreProfileAdminForm(FlaskForm): 
    real_name = StringField('请输入您的真实姓名：', validators=[DataRequired(), Length(1, 64)])
    storename = StringField('请输入您的店铺名称：', validators=[DataRequired(), Length(1, 64)])
    storeaddress = StringField('请输入店铺所在的地址：', validators=[DataRequired(), Length(1, 128)])
    storeimage = FileField('自定义店铺头像（请选择格式为.jpg文件）', validators=[DataRequired()])
    submit = SubmitField('提交更改')

    def __init__(self, user, *args, **kwargs): 
        super(EditStoreProfileAdminForm, self).__init__(*args, **kwargs)
        self.user = user
        self.store = Store.query.filter_by(user_id=self.user.id).first()

    def validate_storename(self, field): 
        if self.store.storename != field.data and Store.query.filter_by(storename=field.data).first(): 
            raise ValidationError('该店铺名已被他人使用！')

class EditStoreCommodityAdminForm(FlaskForm): 
    commodityname = StringField('商品名称：', validators=[DataRequired(), Length(1, 64)])
    inventory = IntegerField('库存量：', validators=[DataRequired()])
    price = FloatField('价格：', validators=[DataRequired()])
    commodity_category = SelectField('商品分类', coerce=int)
    about_commodity = StringField('商品简介：', validators=[Length(0, 128)])
    commodityimage = FileField('自定义商品头像：（请选择格式为.jpg文件）', validators=[DataRequired()])
    submit = SubmitField('提交')

    def __init__(self, *args, **kwargs): 
        super(EditStoreCommodityAdminForm, self).__init__(*args, **kwargs)
        self.commodity_category.choices = [(commodity_category.id, commodity_category.category_name) for commodity_category in Commodity_category.query.order_by(Commodity_category.category_name).all()]

    def validate_inventory(self, field): 
        if field.data < 0: 
            raise ValidationError('库存量必须是正数！')
    
    def validate_price(self, field): 
        if field.data < 0: 
            raise ValidationError('价格必须是正数！')
        if field.data == 0: 
            flash('注意：您将该商品价格设为了0元！')