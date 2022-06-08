from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user
from app.models import User, Department


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Войти', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    form.department.choices = [(dep.id, dep.name) for dep in Department.query.order_by('name').all()]
    if form.validate_on_submit():
        user = User(username=form.username.data, fullname=form.fullname.data,
                    department=get_dep(form.department.data))
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Добавлен новый пользователь!')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', title='Добавить пользователя', form=form)


def get_dep(department_name):
    department = Department.query.filter_by(name=department_name).first()

    if department is None:
        dep = Department(name=department_name)
        try:
            db.session.add(dep)
            db.session.commit()
            return dep
        except:
            return None
    return department
