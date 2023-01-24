from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.auth import bp
from app.auth.forms import RegistrationForm, LoginForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, Grid
from app.auth.email import send_password_reset_email
from werkzeug.security import check_password_hash
from email_validator import validate_email


@bp.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('main.user', username=current_user.username))
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(
                username_id=form.username.data.lower().strip()).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('main.user', username=current_user.username))
        flash(f'Incorrect username or password, please try again.', category='danger')
        return redirect(url_for('auth.login'))
    return render_template('/auth/login.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('main.user', username=current_user.username))
    if request.method == 'POST':
        if form.validate_on_submit():
            newuser = User(form.username.data, form.email.data,
                           form.password.data, form.first_name.data, form.last_name.data)
            try:
                validate_email(form.email.data)
            except:
                flash(
                    f'Sorry, {form.email.data} is not a valid email. Please try again.', category='danger')
                return redirect(url_for('auth.register'))
            try:
                db.session.add(newuser)
                db.session.commit()
            except:
                flash(
                    'Username or email already registered! Please try a different one.', category='danger')
                return redirect(url_for('auth.register'))
            login_user(newuser)
            for i in range(9):
                newgrid = Grid(current_user.id, i)
                db.session.add(newgrid)
                db.session.commit()
            flash(
                f'Welcome "{form.username.data}", Add a bio and some songs to your grid to get started!', category='info')
            return redirect(url_for('main.profile_editor'))
        else:
            flash('Sorry, passwords do not match. Please try again.',
                  category='danger')
            return redirect(url_for('auth.register'))
    elif request.method == 'GET':
        return render_template('/auth/register.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been signed out.', category='info')
    return redirect(url_for('auth.login'))


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.user', username=current_user.username))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('Check your email for instructions to reset password',
                  category='danger')
            return redirect(url_for('auth.login'))
        else:
            flash('Sorry, that email is not registered.', category='danger')
    return render_template('/auth/reset_password_request.html', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.user', username=current_user.username))
    user = User.verify_reset_password_token(token)
    if not user:
        flash('Please request to reset password again', category='danger')
        return redirect(url_for('auth.login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', category='danger')
        return redirect(url_for('auth.login'))
    return render_template('/auth/reset_password.html', form=form)
