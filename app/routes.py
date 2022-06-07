# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Devinfo, Department

status_types = {'Active': 'Активная', 'Return': 'Сдана', 'Broken': 'Вышла из строя'}

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Эльдар Рязанов'}
    devices = [
        {
            'dev_numb': '195-10',
            'dev_id': 'USBSTOR\DISK&VEN_SANDISK&PROD_CRUZER_BLADE&REV_2.01\4C532000010607105025&0',
            'department': {'departmentname': 'Отдел 195'},
            'dev_type': 'USBflash',
            'owner': 'Иванов В. В.',
            'doc_numb': 'с.з. 195/10 от 15.03.2022',
            'status': status_types['Active'],
            'rec_date': '05.06.2022 19:15'
        },
        {
            'dev_numb': '23-1',
            'dev_id': 'USBSTOR\DISK&VEN_SANDISK&PROD_KINGSTONE_BLADE&REV_2.01\4646800005025&0',
            'department': {'departmentname': 'Цех 23'},
            'dev_type': 'USBflash',
            'owner': 'Сидоров М. В.',
            'doc_numb': 'с.з. 23/40 от 11.04.2021',
            'status': status_types['Broken'],
            'rec_date': '11.05.2021 19:15'
        },
        {
            'dev_numb': '119-8',
            'dev_id': 'USBSTOR\DISK&VEN_SANDISK&PROD_CHINE_BLADE&REV_2.01\5667657656553025&0',
            'department': {'departmentname': 'Отдел 119'},
            'dev_type': 'USBflash',
            'owner': 'Кукикова Е. В.',
            'doc_numb': 'с.з. 119/04 от 10.05.2022',
            'status': status_types['Return'],
            'rec_date': '10.06.2022 18:10'
        }
    ]
    return render_template('index.html', title='Список зарегистрированных USB-устройств', devices=devices)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    user = User.query.filter_by(username=form.username.data).first()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        print(user)
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Войти', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, fullname=form.fullname.data,
                    department=get_dep(form.department.data))
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Добавлен новый пользователь!')
        return redirect(url_for('index'))
    return render_template('register.html', title='Добавить пользователя', form=form)


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