from flask_wtf.form import FlaskForm
from wtforms.fields.core import SelectField, StringField
from wtforms.fields.simple import FileField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError
from app.models import Address, Payment, Store, User
from flask_login import current_user

class EditUserAddressForm(FlaskForm): 
    real_name = StringField('收货人', validators=[DataRequired(), Length(1, 64)])
    address = StringField('详细地址', validators=[DataRequired(), Length(1, 128)])
    phone = StringField('手机号码', validators=[DataRequired(), Length(1, 64)])
    submit = SubmitField('保存收货地址')

class EditStoreProfileForm(FlaskForm): 
    real_name = StringField('请输入您的真实姓名：', validators=[DataRequired(), Length(1, 64)])
    storename = StringField('请输入您的店铺名称：', validators=[DataRequired(), Length(1, 64)])
    storeaddress = StringField('请输入店铺所在的地址：', validators=[DataRequired(), Length(1, 128)])
    storeimage = FileField('自定义店铺头像（请选择格式为.jpg文件）', validators=[DataRequired()])
    submit = SubmitField('提交更改')

    def __init__(self, user, *args, **kwargs): 
        super(EditStoreProfileForm, self).__init__(*args, **kwargs)
        self.user = user
        self.store = Store.query.filter_by(user_id=self.user.id).first()

    def validate_storename(self, field): 
        if self.store.storename != field.data and Store.query.filter_by(storename=field.data).first(): 
            raise ValidationError('该店铺名已被他人使用！')

class EditProfileForm(FlaskForm): 
    username = StringField('用户昵称', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, '用户名只能包含字母、数字、.和下划线')])
    avatar = FileField('自定义头像（请选择格式为.jpg文件）', validators=[DataRequired()])
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs): 
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.user = user
        self.username.data = user.username

    def validate_email(self, field): 
        if field.data != self.user.email and User.query.filter_by(email=field.data).first(): 
            raise ValidationError('该邮箱已被注册！')
    
    def validate_username(self, field): 
        if field.data != self.user.username and User.query.filter_by(username=field.data).first(): 
            raise ValidationError('该用户名已被他人使用！')

class EditOrderPaymentForm(FlaskForm): 
    address = SelectField('收货人信息：', coerce=int)
    payment = SelectField('支付方式：', coerce=int)
    submit = SubmitField('提交订单')

    def __init__(self, *args, **kwargs): 
        super(EditOrderPaymentForm, self).__init__(*args, **kwargs)
        self.address.choices = [(address.id, address.real_name + ' ' + address.address + ' ' + address.phone) for address in Address.query.filter_by(user_id=current_user.id).all()]
        self.payment.choices = [(payment.id, payment.paymentname) for payment in Payment.query.all()]