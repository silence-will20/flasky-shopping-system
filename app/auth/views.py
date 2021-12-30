from threading import currentThread
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.auth.forms import LoginForm
from . import auth
from ..models import Store, User
from .forms import LoginForm, RegisterForm, RegisterStore, ResetPasswordForm
from .. import db, storeimages
from ..email import send_email
from flask_login import current_user
import os

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit(): 
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data): 
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'): 
                next = url_for('main.index')
            return redirect(next)
        flash('用户名或密码错误')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout(): 
    logout_user()
    flash('你已成功登出')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register(): 
    form = RegisterForm()
    if form.validate_on_submit(): 
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        if user.confirmed == False: 
            send_email(user.email, '确认您的账户', 'auth/email/confirm', user=user, token=token)
        flash('注册成功，系统已为您发送确认邮件，请在注册邮箱中查看并将您的账户激活！')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password(): 
    form = ResetPasswordForm()
    if form.validate_on_submit(): 
        user = User.query.get(current_user.id)
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        flash('密码修改成功，请重新登录！')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token): 
    if current_user.confirmed: 
        return redirect(url_for('main.index'))
    if current_user.confirm(token): 
        db.session.commit()
        flash('感谢使用，您的账户已经成功激活！')
    else: 
        flash('该确认链接无效或已经过期！')
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_request(): 
    if current_user.is_authenticated and not current_user.confirmed and request.blueprint != 'main' and request.blueprint != 'auth' and request.endpoint != 'static': 
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
@login_required
def unconfirmed(): 
    if current_user.is_anonymous or current_user.confirmed: 
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html', username=current_user.username)

@auth.route('/confirm')
@login_required
def resend_confirmation(): 
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '确认您的账户', 'auth/email/confirm', user=current_user, token=token)
    flash('已经向您发送确认邮件，请在一小时内完成确认操作')
    return redirect(url_for('main.index'))

@auth.route('/register-store', methods=['GET', 'POST'])
@login_required
def register_store(): 
    form = RegisterStore()
    if Store.query.filter_by(user_id=current_user.id).first(): 
        flash('您已经是商家用户了，请勿重复申请！')
        return redirect('user.user_profile')
    if form.validate_on_submit(): 
        user_id = current_user.id
        real_name = form.real_name.data
        storename = form.storename.data
        storeaddress = form.storeaddress.data
        about_store = form.about_store.data
        try:
            filename = storeimages.save(request.files['storeimage'], name=f"{current_user.id}.")
        except: 
            flash('头像上传失败，请重试！')
            return render_template('register_store.html', form=form)
        storeimage = filename
        store = Store(user_id=user_id, real_name=real_name, storename=storename, storeaddress=storeaddress, storeimage=storeimage, about_store=about_store)
        user = User.query.get(current_user.id)
        user.role_id = 2
        current_user.role_id = 2
        db.session.add(store)
        db.session.add(user)
        db.session.commit()
        flash('您已成功注册为商家用户，可以对您的店铺进行管理！')
        return redirect(url_for('user.user_store_profile'))
    return render_template('auth/register_store.html', form=form)