from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import User, db, Grid
from werkzeug.security import check_password_hash
from flask_login import login_user, current_user, login_required, logout_user

auth = Blueprint('auth', __name__, template_folder='auth_templates',static_folder='auth_static')

from .authforms import RegistrationForm, LoginForm

@auth.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('user', username=current_user.username))
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(username_id=form.username.data.lower()).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('user', username=current_user.username))
        flash(f'Incorrect username or password, please try again.', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('user', username=current_user.username))
    if request.method == 'POST':
        if form.validate_on_submit():
            newuser = User(form.username.data, form.email.data, form.password.data, form.first_name.data, form.last_name.data)
            try:
                db.session.add(newuser)
                db.session.commit()
            except:
                flash('Username or email already registered! Please try a different one.', category='danger')
                return redirect(url_for('auth.register'))
            login_user(newuser)
            for i in range(9):
                newgrid = Grid(current_user.id,i)
                db.session.add(newgrid)
                db.session.commit()
            return redirect(url_for('user', username=current_user.username))
        else:
            flash('Sorry, passwords do not match. Please try again.', 'danger')
            return redirect(url_for('auth.register'))
    elif request.method == 'GET':
        return render_template('register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been signed out.', 'info')
    return redirect(url_for('auth.login'))