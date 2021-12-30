from flask_wtf.form import FlaskForm
from wtforms.fields.core import FloatField, IntegerField, SelectField, StringField
from wtforms.fields.simple import FileField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from flask import flash
from ..models import Commodity_category

class EditStoreCommodityForm(FlaskForm): 
    commodityname = StringField('商品名称：', validators=[DataRequired(), Length(1, 64)])
    inventory = IntegerField('库存量：', validators=[DataRequired()])
    price = FloatField('价格：', validators=[DataRequired()])
    commodity_category = SelectField('商品分类', coerce=int)
    about_commodity = StringField('商品简介：', validators=[Length(0, 128)])
    commodityimage = FileField('自定义商品头像：（请选择格式为.jpg文件）', validators=[DataRequired()])
    submit = SubmitField('提交')

    def __init__(self, *args, **kwargs): 
        super(EditStoreCommodityForm, self).__init__(*args, **kwargs)
        self.commodity_category.choices = [(commodity_category.id, commodity_category.category_name) for commodity_category in Commodity_category.query.order_by(Commodity_category.category_name).all()]

    def validate_inventory(self, field): 
        if field.data < 0: 
            raise ValidationError('库存量必须是正数！')
    
    def validate_price(self, field): 
        if field.data < 0: 
            raise ValidationError('价格必须是正数！')
        if field.data == 0: 
            flash('注意：您将该商品价格设为了0元！')