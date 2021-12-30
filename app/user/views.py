import os
from flask.helpers import flash, url_for
from flask.templating import render_template
from flask_login.utils import login_required, current_user
from werkzeug.utils import redirect
from app.decorators import permission_required
from app.models import Address, Basket, Commodity, Order, Payment, Permission, Store, User
from flask import request
from datetime import datetime
from .forms import EditOrderPaymentForm, EditProfileForm, EditStoreProfileForm, EditUserAddressForm
from . import user
from .. import db, avatars, storeimages

@user.route('/<username>')
@login_required
def my_user(username): 
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user/user.html', user=user)

@user.route('/profile')
@login_required
def user_profile(): 
    return render_template('user/profile.html')

@user.route('/address')
@login_required
def user_address(): 
    address = Address.query.filter_by(user_id=current_user.id).all()
    return render_template('user/address.html', address=address)

@user.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile(): 
    form = EditProfileForm(current_user)
    if form.validate_on_submit(): 
        current_user.username = form.username.data
        try:
            path = os.path.join(avatars.path(''), '{}.jpg'.format(current_user.id))
            if os.path.exists(path):  # 如果文件存在
                os.remove(path)  # 删除文件
            filename = avatars.save(request.files['avatar'], name=f"{current_user.id}.")
        except: 
            flash('头像上传失败，请重试！')
            return render_template('user/edit_profile.html', form=form, user=current_user)
        current_user.avatar = filename
        db.session.add(current_user)
        db.session.commit()
        flash('账户信息更新成功')
        return redirect(url_for('.my_user', username=current_user.username))
    form.username.data = current_user.username
    return render_template('user/edit_profile.html', form=form, user=current_user)


@user.route('/user-add-address', methods=['GET', 'POST'])
@login_required
def user_add_address(): 
    form = EditUserAddressForm()
    if form.validate_on_submit(): 
        user_id = current_user.id
        address = form.address.data
        phone = form.phone.data
        real_name = form.real_name.data
        address = Address(user_id=user_id, address=address, phone=phone, real_name=real_name)
        db.session.add(address)
        db.session.commit()
        return redirect(url_for('.user_address'))
    return render_template('user/edit_address.html', form=form)

@user.route('/user-edit-address/<addressid>', methods=['GET', 'POST'])
@login_required
def user_edit_address(addressid): 
    form = EditUserAddressForm()
    address = Address.query.get(addressid)
    if form.validate_on_submit(): 
        address.user_id = current_user.id
        address.address = form.address.data
        address.phone = form.phone.data
        address.real_name = form.real_name.data
        db.session.add(address)
        db.session.commit()
        return redirect(url_for('.user_address'))
    form.address.data = address.address
    form.phone.data = address.phone
    address.real_name = address.real_name
    return render_template('user/edit_address.html', form=form)

@user.route('/user/user-delete-address/<addressid>')
@login_required
def user_delete_address(addressid):
    address = Address.query.get(addressid) 
    if current_user.id == address.user_id: 
        db.session.delete(address)
        db.session.commit()
        return redirect(url_for('.user_address'))
    else: 
        flash('您没有权限进行此操作！')
        address = Address.query.filter_by(user_id=current_user.id).all()
    return render_template('user/address.html', address=address)

@user.route('/store-profile')
@login_required
@permission_required(Permission.SALE)
def user_store_profile(): 
    store = Store.query.filter_by(user_id=current_user.id).first()
    return render_template('user/user_store_profile.html', store=store)

@user.route('/user/edit-store-profile', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.SALE)
def edit_store_profile(): 
    store = Store.query.filter_by(user_id=current_user.id).first()
    form = EditStoreProfileForm(current_user)
    if form.validate_on_submit(): 
        store.real_name = form.real_name.data
        store.storename = form.storename.data
        store.storeaddress = form.storeaddress.data
        try:
            path = os.path.join(storeimages.path(''), '{}.jpg'.format(current_user.id))
            if os.path.exists(path):  # 如果文件存在
                os.remove(path)  # 删除文件
            filename = storeimages.save(request.files['storeimage'], name=f"{current_user.id}.")
        except: 
            flash('头像上传失败，请重试！')
            return render_template('auth/register_store.html', form=form)
        store.storeimage = filename
        db.session.add(store)
        db.session.commit()
        flash('店铺信息更新成功！')
        return redirect(url_for('.user_store_profile'))
    form.real_name.data = store.real_name
    form.storename.data = store.storename
    form.storeaddress.data = store.storeaddress
    return render_template('user/edit_store_profile.html', form=form)

@user.route('/my-basket')
@login_required
def my_basket(): 
    basket = Basket.query.filter_by(user_id=current_user.id).all()
    stores = []
    commodities = []
    total_price = 0
    for b in basket:
        commodity = Commodity.query.get(b.commodity_id)
        stores.append(commodity.store.storename)
        commodities.append(commodity)
        total_price += commodity.price * b.number
    count = len(stores)
    return render_template('user/my_basket.html', stores=stores, commodities=commodities, basket=basket, count=count, total_price=total_price)

@user.route('/add-commodity-to-basket/<commodityid>', methods=['GET', 'POSt'])
@login_required
def add_commodity_to_basket(commodityid): 
    basket = Basket.query.filter_by(user_id=current_user.id, commodity_id=commodityid).first()
    if basket: 
        if request.form: 
            basket.number = basket.number + (int(request.form['purchase_quantity']))
        else: 
            basket.number = basket.number + 1
        db.session.add(basket)
        db.session.commit()
    else: 
        if request.form: 
            number = request.form['purchase_quantity']
        else: 
            number = 1
        user_id = current_user.id
        basket = Basket(user_id=user_id, commodity_id=commodityid, number=number)
        db.session.add(basket)
        db.session.commit()
    recommending_commodities = Commodity.query.order_by(Commodity.sales_volume).limit(6)
    commodity = Commodity.query.get(commodityid)
    store_commodities = Commodity.query.filter_by(store_id=commodity.store_id).all()
    s = Store.query.get(commodity.store_id)
    storekeeper = User.query.get(commodity.store.user_id)
    flash('商品已成功添加到购物车！')
    return render_template('commodity_detail.html', store_commodities=store_commodities, commodity=commodity, recommending_commodities=recommending_commodities, storekeeper=storekeeper, basket=basket, s=s)

@user.route('/delete-commodity-from-basket/<commodityid>')
@login_required
def delete_commodity_from_basket(commodityid): 
    basket = Basket.query.filter_by(user_id=current_user.id, commodity_id=commodityid).first()
    db.session.delete(basket)
    db.session.commit()
    flash('该商品已从购物车删除！')
    basket = Basket.query.filter_by(user_id=current_user.id).all()
    stores = []
    commodities = []
    total_price = 0
    for b in basket:
        commodity = Commodity.query.get(b.commodity_id)
        stores.append(commodity.store.storename)
        commodities.append(commodity)
        total_price += commodity.price * b.number
    count = len(stores)
    return render_template('user/my_basket.html', stores=stores, commodities=commodities, basket=basket, count=count, total_price=total_price)

@user.route('/comfirm-order', methods=['GET', 'POST'])
@login_required
def confirm_order(): 
    if not current_user.addresses: 
        flash('请先添加收货地址后再下单！')
        return redirect(url_for('user.user_add_address'))
    form = EditOrderPaymentForm()
    basket = Basket.query.filter_by(user_id=current_user.id).all()
    if form.validate_on_submit(): 
        user_id = current_user.id
        time = datetime.utcnow()
        ads = Address.query.get(form.address.data)
        address = ads.real_name + ' ' + ads.address + ' ' + ads.phone
        payment_id = form.payment.data
        for b in basket: 
            commodity = Commodity.query.get(b.commodity_id)
            if b.number > commodity.inventory: 
                flash('商品{}库存量已不足，请将商品重新添加购物车后再次购买！'.format(commodity.commodityname))
                return redirect(url_for('.my_orders'))
            price = commodity.price * b.number
            store_id = commodity.store.id
            order = Order(user_id=user_id, time=time, commodity_id=b.commodity_id, address=address, payment_id=payment_id, price=price, store_id=store_id, number=b.number)
            order.store = commodity.store
            order.payment = Payment.query.get(payment_id)
            db.session.add(order)
            flash('您的订单已成功生成')
            commodity.sales_volume += order.number
            commodity.inventory -= order.number
            db.session.add(commodity)
            db.session.commit()
        return redirect(url_for('.my_orders'))
    total_price = 0
    for b in basket: 
        commodity = Commodity.query.get(b.commodity_id)
        total_price += commodity.price * b.number 
    return render_template('user/confirm_order.html', form=form, total_price=total_price)

@user.route('/my-orders')
@login_required
def my_orders(): 
    orders = Order.query.filter_by(user_id=current_user.id).all()
    stores = []
    commodities = []
    for order in orders:
        commodity = Commodity.query.get(order.commodity_id)
        stores.append(commodity.store.storename)
        commodities.append(commodity)
    count = len(stores)
    return render_template('user/my_orders.html', orders=orders, count=count, stores=stores, commodities=commodities)

@user.route('/delete-order/<orderid>')
@login_required
def delete_order(orderid): 
    order = Order.query.get(orderid)
    commodity = Commodity.query.get(order.commodity_id)
    commodity.sales_volume -= order.number
    commodity.inventory += order.number
    db.session.add(commodity)
    db.session.delete(order)
    db.session.commit()
    flash('已成功取消订单！')
    orders = Order.query.filter_by(user_id=current_user.id).all()
    stores = []
    commodities = []
    for order in orders:
        commodity = Commodity.query.get(order.commodity_id)
        stores.append(commodity.store.storename)
        commodities.append(commodity)
    count = len(stores)
    return render_template('user/my_orders.html', orders=orders, count=count, stores=stores, commodities=commodities)