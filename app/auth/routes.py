import random
import string
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from . import auth_bp
from .forms import (RegistrationForm, EditUserForm, LoginForm, 
                    ChangeGeneratedPasswordForm, ForgotPasswordForm, ForgotUsernameForm)
from ..extensions import db, bcrypt, mail
from ..models import User, Role
from ..utils.utility_functions import admin_required

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("An account with this email already exists.", "danger")
            return render_template("register.html", form=form)
        
        existing_username = User.query.filter_by(username=form.username.data).first()
        if existing_username:
            flash("This username is already taken.", "danger")
            return render_template("register.html", form=form)

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user_role = Role.query.filter_by(name='user').first()
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            dob=form.dob.data,
            phone_number=form.phone_number.data,
            role=user_role,
            in_store_credit=0
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_bp.route('/edit_user', methods=['GET', 'POST'])
@login_required
def edit_user():
    form = EditUserForm(obj=current_user)
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.dob = form.dob.data
        current_user.phone_number = form.phone_number.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('main.home'))
    return render_template('edit_user.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(
            (User.email == form.username_or_email.data) | 
            (User.username == form.username_or_email.data)
        ).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            if user.PasswordReset:
                return redirect(url_for('auth.change_generated_password'))
            return redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check username/email and password', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/change_generated_password', methods=['GET', 'POST'])
@login_required
def change_generated_password():
    if not current_user.PasswordReset:
        return redirect(url_for('main.home'))
    form = ChangeGeneratedPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
        current_user.password_hash = hashed_password
        current_user.PasswordReset = 0
        db.session.commit()
        flash('Your password has been updated.', 'success')
        return redirect(url_for('main.home'))
    return render_template('change_generated_password.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter(
            (User.email == form.username_or_email.data) |
            (User.username == form.username_or_email.data)
        ).first()
        if user:
            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
            user.PasswordReset = 1
            db.session.commit()
            msg = Message('Password Reset', recipients=[user.email])
            msg.body = f'Your new password is: {new_password}'
            mail.send(msg)
            flash('A new password has been sent to your email.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('No user found with that username or email.', 'danger')
    return render_template('forgot_password.html', form=form)

@auth_bp.route('/forgot_username', methods=['GET', 'POST'])
def forgot_username():
    form = ForgotUsernameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            msg = Message('Username Retrieval', recipients=[user.email])
            msg.body = f'Your username is: {user.username}'
            mail.send(msg)
            flash('Your username has been sent to your email.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('No user found with that email.', 'danger')
    return render_template('forgot_username.html', form=form)

@auth_bp.route('/account')
@login_required
def account():
    return render_template('account.html', user=current_user)
