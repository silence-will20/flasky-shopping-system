from threading import current_thread
from flask_wtf import FlaskForm
from flask_wtf.form import SUBMIT_METHODS
from flask_login import current_user
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import ValidationError
from wtforms import validators
from wtforms.fields.simple import FileField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from ..models import Store, User

class LoginForm(FlaskForm): 
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

class RegisterForm(FlaskForm): 
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
        '用户名只能包含字母、数字、.和下划线')])
    password = PasswordField('密码', validators=[DataRequired(), EqualTo('password2', message='两次输入的密码必须一致')])
    password2  = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self, field): 
        if User.query.filter_by(email=field.data).first(): 
            raise ValidationError('该邮箱已被注册！')
    
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first(): 
            raise ValidationError('该用户名已被他人使用！')

class RegisterStore(FlaskForm): 
    real_name = StringField('请输入您的真实姓名：', validators=[DataRequired(), Length(1, 64)])
    storename = StringField('请输入您的店铺名称：', validators=[DataRequired(), Length(1, 64)])
    storeaddress = StringField('请输入店铺所在的地址：', validators=[DataRequired(), Length(1, 128)])
    about_store = StringField('店铺简介：', validators=[Length(0, 128)])
    storeimage = FileField('自定义店铺头像（请选择格式为.jpg文件）', validators=[DataRequired()])
    
    submit = SubmitField('提交申请')
    
    def validate_storename(self, field): 
        if Store.query.filter_by(storename=field.data).first(): 
            raise ValidationError('该店铺名已被他人使用！')

class ResetPasswordForm(FlaskForm): 
    oldpassword = PasswordField('旧密码', validators=[DataRequired()])
    password = PasswordField('新密码', validators=[DataRequired(), EqualTo('password2', message='两次输入的密码必须一致')])
    password2  = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('确认修改')

    def validate_oldpassword(self, field): 
        if not check_password_hash(current_user.password_hash, field.data): 
            raise ValidationError('旧密码输入错误！')
    
    def validate_password(self, field): 
        if check_password_hash(generate_password_hash(self.oldpassword.data), field.data):
            raise ValidationError('新密码旧密码不能一致！')