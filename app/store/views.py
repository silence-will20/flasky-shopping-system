import os
from flask.helpers import flash, url_for
from flask.templating import render_template
from flask_login.utils import login_required
from flask_login import current_user
from flask import request
from werkzeug.utils import redirect
from app.decorators import permission_required
from app.models import Commodity, Commodity_category, Order, Permission, Store
from .forms import EditStoreCommodityForm
from . import store
from .. import db, commodityimages
import random, string


@store.route('/manage-commodities')
@login_required
@permission_required(Permission.SALE)
def manage_commodities(): 
    store = Store.query.filter_by(user_id=current_user.id).first()
    commodities = Commodity.query.filter_by(store_id=store.id).all()
    category_name = []
    for com in commodities: 
        category_name.append(com.commodity_category.category_name)
    commodity_and_category = list(zip(commodities, category_name))
    return render_template('store/manage_commodities.html', commodity_and_category=commodity_and_category, user=current_user)

@store.route('/store-add-commodity', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.SALE)
def store_add_commodity(): 
    store = Store.query.filter_by(user_id=current_user.id).first()
    form = EditStoreCommodityForm()
    if form.validate_on_submit(): 
        store_id = store.id
        commodityname = form.commodityname.data
        price = form.price.data
        inventory = form.inventory.data
        about_commodity = form.about_commodity.data
        try:
            filename = commodityimages.save(request.files['commodityimage'], name=''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))+'.jpg')
        except: 
            flash('头像上传失败，请重试！')
            return render_template('store/edit_store_commodity.html', form=form)
        commodityimage = filename
        commodity_category = Commodity_category.query.get(form.commodity_category.data)
        commodity = Commodity(store_id=store_id, commodity_category_id=commodity_category.id, price=price, inventory=inventory, about_commodity=about_commodity, commodityname=commodityname, commodityimage=commodityimage)
        commodity.commodity_category = commodity_category
        db.session.add(commodity)
        db.session.commit()
        flash('商品上架成功！')
        return redirect(url_for('.manage_commodities'))
    return render_template('store/edit_store_commodity.html', form=form)

@store.route('/store-edit-commodity/<commodityid>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.SALE)
def store_edit_commodity(commodityid): 
    store = Store.query.filter_by(user_id=current_user.id).first()
    form = EditStoreCommodityForm()
    commodity = Commodity.query.get(commodityid)
    if form.validate_on_submit(): 
        commodity.store_id = store.id
        commodity.commodityname = form.commodityname.data
        commodity.price = form.price.data
        commodity.inventory = form.inventory.data
        commodity.about_commodity = form.about_commodity.data
        try:
            path = os.path.join(commodityimages.path(''), commodity.commodityimage)
            if os.path.exists(path):  # 如果文件存在
                os.remove(path)  # 删除文件
            filename = commodityimages.save(request.files['commodityimage'], name=f"{commodity.commodityimage}")
        except: 
            flash('头像上传失败，请重试！')
            return render_template('store/edit_store_commodity.html', form=form)
        commodity.commodityimage = filename
        commodity_category = Commodity_category.query.get(form.commodity_category.data)
        commodity.commodity_category = commodity_category
        db.session.add(commodity)
        db.session.commit()
        flash('商品信息已成功修改！')
        return redirect(url_for('.manage_commodities'))
    form.commodityname.data = commodity.commodityname
    form.price.data = commodity.price
    form.inventory.data = commodity.inventory
    form.commodity_category.data = commodity.commodity_category_id
    form.about_commodity.data = commodity.about_commodity
    return render_template('store/edit_store_commodity.html', form=form)

@store.route('/store-delete-commodity/<commodityid>')
@login_required
@permission_required(Permission.SALE)
def store_delete_commodity(commodityid): 
    commodity = Commodity.query.get(commodityid)
    if current_user.id == commodity.store.user_id: 
        db.session.delete(commodity)
        db.session.commit()
        path = os.path.join(commodityimages.path(''), commodity.commodityimage)
        if os.path.exists(path):  # 如果文件存在
            os.remove(path)  # 删除文件
        flash('该商品已成功下架！')
        return redirect(url_for('.manage_commodities'))
    else: 
        flash('您没有权限进行此操作！')
        commodities = Commodity.query.filter_by(store_id=commodity.store.id).all()
        category_name = []
        for com in commodities: 
            category_name.append(com.commodity_category.category_name)
        commodity_and_category = list(zip(commodities, category_name))
        return render_template('store/manage_commodities.html', commodity_and_category=commodity_and_category)

@store.route('/manage-user-orders')
@login_required
@permission_required(Permission.SALE)
def manage_user_orders(): 
    store = Store.query.filter_by(user_id=current_user.id).first()
    #orders = store.orders
    orders = Order.query.filter_by(store_id=store.id).all()
    count = 0
    users = []
    commodities = []
    for order in orders: 
        users.append(order.user)
        commodities.append(order.commodity)
        count += 1
    return render_template('store/manage_user_orders.html', users=users, orders=orders, count=count, commodities=commodities)

@store.route('/store-detail/<storeid>')
def store_detail(storeid): 
    store = Store.query.get(storeid)
    return render_template('store/store_detail.html', store=store)