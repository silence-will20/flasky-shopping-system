import os
from flask.helpers import flash, url_for
from flask.templating import render_template
from flask_login.utils import login_required
from werkzeug.utils import redirect
from app.admin.forms import EditProfileAdminForm, EditStoreCommodityAdminForm, EditStoreProfileAdminForm, EditUserProfileAdminForm
from flask_login import current_user
from flask import request
from app.decorators import admin_required
from app.models import Commodity, Commodity_category, Role, Store, User
from . import admin
from .. import db, storeimages, commodityimages

@admin.route('/edit-user-profile/get-userid', methods=['GET', 'POST'])
@login_required
@admin_required
def get_userid(): 
    form = EditUserProfileAdminForm()
    if form.validate_on_submit(): 
        user = User.query.filter_by(email=form.email.data).first()
        if user != None: 
            return redirect(url_for('.edit_profile_admin', userid=user.id))
        else: 
            flash('该邮箱尚未注册！')
            form.email.data = None
    return render_template('admin/get_userid.html', form=form)

@admin.route('/edit-user-profile/<userid>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(userid): 
    user = User.query.get_or_404(userid)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit(): 
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('该用户资料已成功变更')
        return redirect(url_for('user.my_user', username=current_user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    return render_template('user/edit_profile.html', form=form, user=user)

@admin.route('/edit-store-profile/<userid>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_store_profile(userid): 
    store = Store.query.filter_by(user_id=userid).first()
    user = store.user
    form = EditStoreProfileAdminForm(user)
    if form.validate_on_submit(): 
        store.real_name = form.real_name.data
        store.storename = form.storename.data
        store.storeaddress = form.storeaddress.data
        try:
            path = os.path.join(storeimages.path(''), '{}.jpg'.format(user.id))
            if os.path.exists(path):  # 如果文件存在
                os.remove(path)  # 删除文件
            filename = storeimages.save(request.files['storeimage'], name=f"{user.id}.")
        except: 
            flash('头像上传失败，请重试！')
            return render_template('user/edit_store_profile.html', form=form, user=user)
        store.storeimage = filename
        db.session.add(store)
        db.session.commit()
        flash('店铺信息更新成功！')
        return redirect(url_for('admin.edit_profile_admin', userid=userid))
    form.real_name.data = store.real_name
    form.storename.data = store.storename
    form.storeaddress.data = store.storeaddress
    return render_template('user/edit_store_profile.html', form=form, user=user)

@admin.route('/manage-store-commodities/<userid>', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_store_commodities(userid): 
    store = Store.query.filter_by(user_id=userid).first()
    commodities = Commodity.query.filter_by(store_id=store.id).all()
    category_name = []
    for com in commodities: 
        category_name.append(com.commodity_category.category_name)
    commodity_and_category = list(zip(commodities, category_name))
    return render_template('admin/manage_store_commodities.html', commodity_and_category=commodity_and_category, user=store.user)

@admin.route('/admin-store-edit-commodity/<userid>/<commodityid>', methods=['GET', 'POST'])
@login_required
@admin_required
def store_edit_commodity(userid, commodityid): 
    store = Store.query.filter_by(user_id=userid).first()
    form = EditStoreCommodityAdminForm()
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
        return redirect(url_for('.manage_store_commodities', userid=userid))
    form.commodityname.data = commodity.commodityname
    form.price.data = commodity.price
    form.inventory.data = commodity.inventory
    form.commodity_category.data = commodity.commodity_category_id
    form.about_commodity.data = commodity.about_commodity
    return render_template('store/edit_store_commodity.html', form=form)

@admin.route('/admin-store-delete-commodity/<userid>/<commodityid>', methods=['GET', 'POST'])
@login_required
@admin_required
def store_delete_commodity(userid, commodityid): 
    commodity = Commodity.query.get(commodityid)
    store = commodity.store
    db.session.delete(commodity)
    db.session.commit()
    path = os.path.join(commodityimages.path(''), commodity.commodityimage)
    if os.path.exists(path):  # 如果文件存在
        os.remove(path)  # 删除文件
    flash('该商品已成功下架！')
    commodities = Commodity.query.filter_by(store_id=store.id).all()
    category_name = []
    for com in commodities: 
        category_name.append(com.commodity_category.category_name)
    commodity_and_category = list(zip(commodities, category_name))
    return render_template('admin/manage_store_commodities.html', commodity_and_category=commodity_and_category, user=commodity.store.user)