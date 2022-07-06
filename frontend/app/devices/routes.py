# -*- coding: utf-8 -*-
import json
from frontend import app
from flask import render_template, redirect, url_for, request, flash
from app.devices.forms import FilterForm, EditForm, AddForm
from app import Config
from app.devices import bp
from app.token import token_401, make_token_headers
from datetime import datetime
import requests
import os.path
from werkzeug.utils import secure_filename


# func view for showing all devices
@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@bp.route('/devices_all', methods=['GET', 'POST'])
def devices_all():
    # check token in cookie
    if request.cookies.get('token'):
        # make request for last recording of all devices
        # successful result: dict_dep_dev - dict contains two key:
        # departments - id and name of all departments
        # devices - last recording about all devices
        dict_dep_dev = requests.get(f'{Config.BACKEND_ADDRESS}/api/v1/devices/all', headers=make_token_headers()).json()
        # check result dict_dep_dev
        if 'error' in dict_dep_dev:
            # 401 code error. Our token is dead
            if dict_dep_dev['error'] == 'Unauthorized':
                return token_401(
                    "Срок действия Вашего токена истек. Повторите вход.")
            # if other error which we didn't expect - create flash mes with category devices_all
            # and refresh page with flash mes
            else:
                flash('Операция не выполнена: ' + dict_dep_dev['error'], 'devices_all')
                return redirect(url_for('devices.devices_all'))
        elif 'message' in dict_dep_dev:
            flash(dict_dep_dev['message'], 'devices_all')
            return redirect(url_for('devices.devices_all'))
        # create form for filtering devices
        filter_form = FilterForm()
        # full select field of departments
        # k - id department
        # v - name department
        filter_form.department_id.choices = filter_form.department_id.choices + \
                                            [(k, v) for k, v in dict_dep_dev["departments"].items()]
        # get dict of devices from list_dep_dev
        devices = dict_dep_dev["devices"]
        # POST
        if filter_form.validate_on_submit():
            # push button to apply filter
            if filter_form.submit_apply.data:
                # create dict with filtering params:
                # k - field's name
                # v - data in field
                filter_params = {k: v for k, v in filter_form.data.items()
                                 if filter_form.data[k] and filter_form.data[k] != 'None'}
                # make a request to get filtered devices
                # redefine above variable devices
                devices = requests.get(f'{Config.BACKEND_ADDRESS}/api/v1/devices/all/with_filter',
                                       data=json.dumps(filter_params, ensure_ascii=False).encode('utf8'),
                                       headers=make_token_headers()).json()
                # check result in devices
                if 'error' in devices:
                    # 401 code error. Our token is dead
                    if devices['error'] == 'Unauthorized':
                        return token_401(
                            "Срок действия Вашего токена истек. Повторите вход.")
                    # if other error which we didn't expect - create flash mes with category devices_all
                    # and refresh page with flash mes
                    else:
                        flash('Операция не выполнена: ' + devices['error'], 'devices_all')
                        return redirect(url_for('devices.devices_all'))
                elif 'message' in devices:
                    flash(devices['message'], 'devices_all')
                    return redirect(url_for('devices.devices_all'))
            # push button clear - just refresh page with clear filter form
            if filter_form.submit_clear.data:
                return redirect(url_for('devices.devices_all'))

        format = '%Y-%m-%d %H:%M:%S'
        for dev in devices:
            # transform string date to datetime obj for correct display data on page with using
            # flask lib moment
            dev['rec_date'] = datetime.strptime(dev['rec_date'], format)
            # transform dev_id to url_dev_id by replace \ to * for using dev_id as
            # get-argument for page Detail
            # and add new key - url_dev_id
            dev['url_dev_id'] = dev_id_to_url(dev['dev_id'])

        return render_template('devices/devices_all.html', title='Список зарегистрированных USB-устройств',
                               devices=devices, form=filter_form)
    else:
        return redirect(url_for('auth.login'))


@bp.route('/devices/detail/<string:url_dev_id>')
def device_detail(url_dev_id):
    if request.cookies.get('token'):
        dev_id = url_to_dev_id(url_dev_id)
        dev_detail = requests.get(f'{Config.BACKEND_ADDRESS}/api/v1/devices/detail',
                                  headers=make_token_headers(),
                                  data=json.dumps({'dev_id': dev_id})).json()
        if 'error' in dev_detail:
            if dev_detail['error'] == 'Unauthorized':
                return token_401("Срок действия Вашего токена истек. Повторите вход.")
        format = '%Y-%m-%d %H:%M:%S'
        for dev in dev_detail:
            dev['rec_date'] = datetime.strptime(dev['rec_date'], format)
            dev['url_dev_id'] = dev_id_to_url(dev['dev_id'])
        return render_template("devices/device_detail.html", dev_detail=dev_detail,
                               title=f'Устройство: {dev_id}')
    else:
        return redirect(url_for('auth.login'))


@bp.route('/devices/del_all_data/<string:url_dev_id>')
def device_delete_all(url_dev_id):
    if request.cookies.get('token'):
        del_detail = requests.delete(f'{Config.BACKEND_ADDRESS}/api/v1/devices/del_all_data/{url_dev_id}',
                                     headers=make_token_headers())

        if del_detail.status_code == 204:
            flash(f'Все данные об устройстве удалены успешно', 'devices')
            return redirect(url_for('devices.devices_all'))
        elif del_detail.status_code == 401:
            return token_401("Срок действия Вашего токена истек. Данные об устройстве не удалены.")
        else:
            flash(f'При удалении всех записей об устройстве произошла ошибка: {del_detail.status_code}', 'devices')
            return redirect(url_for('devices.devices_all'))
    else:
        return redirect(url_for('auth.login'))


@bp.route('/devices/del_rec/<int:id>')
def device_delete_rec(id):
    if request.cookies.get('token'):
        url_dev_id = request.args.get('url_dev_id', None)
        del_rec = requests.delete(f'{Config.BACKEND_ADDRESS}/api/v1/devices/del_rec/{id}',
                                  headers=make_token_headers())

        if del_rec.status_code == 204:
            flash(f'Запись удалена успешно', 'devices')
            return redirect(url_for('devices.device_detail', url_dev_id=url_dev_id))
        elif del_rec.status_code == 401:
            return token_401("Срок действия Вашего токена истек. Запись об устройтсве не удалена.")
        else:
            flash(f'При удалении записи об устройстве произошла ошибка: {del_rec.status_code}', 'devices')
            return redirect(url_for('devices.device_detail', url_dev_id=url_dev_id))
    else:
        return redirect(url_for('auth.login'))


@bp.route('/devices/correct_rec/<int:id>', methods=['GET', 'POST'])
def device_correct_rec(id):
    if request.cookies.get('token'):
        all_departments = requests.get(Config.BACKEND_ADDRESS + "/api/v1/department/all",
                                       headers=make_token_headers())
        if all_departments.status_code == 401:
            return token_401("Срок действия Вашего токена истек. Повторите вход.")
        rec_for_edit = requests.get(f'{Config.BACKEND_ADDRESS}/api/v1/devices/{id}',
                                    headers=make_token_headers()).json()
        if 'error' in rec_for_edit:
            if rec_for_edit['error'] == 'Unauthorized':
                return token_401('Срок действия Вашего токена истек. Повторите вход.')
            elif 'message' in rec_for_edit:
                flash(rec_for_edit['message'], 'correct_rec_dev')
                return redirect(url_for('devices.device_correct_rec', id=id))

        form = EditForm(original_dict={'dev_numb': rec_for_edit['dev_numb'], 'dev_id': rec_for_edit['dev_id'],
                                       'department_id': str(rec_for_edit['department_id']),
                                       'owner': rec_for_edit['owner'],
                                       'doc_numb': rec_for_edit['doc_numb'], 'status': rec_for_edit['status'],
                                       'remark': rec_for_edit['remark'], 'dev_type': rec_for_edit['dev_type']})
        form.department_id.choices = [(k, v) for k, v in all_departments.json().items()]

        if form.validate_on_submit():
            put_fields = {}
            for form_name, val in form.original_dict.items():
                if form[form_name].data != val:
                    put_fields[form_name] = form[form_name].data

            if len(put_fields) != 0:
                put_dev_rec = requests.put(f'{Config.BACKEND_ADDRESS}/api/v1/devices/{id}',
                                           data=json.dumps(put_fields, ensure_ascii=False).encode('utf8'),
                                           headers=make_token_headers()).json()
                if 'error' in put_dev_rec:
                    if put_dev_rec['error'] == 'Unauthorized':
                        return token_401(
                            "Данные пользователя не изменены. Срок действия Вашего токена истек. Повторите вход.")
                    elif 'message' in put_dev_rec:
                        flash(put_dev_rec['message'], 'correct_rec_dev')
                        return redirect(url_for('devices.device_correct_rec', id=id))
                if 'dev_id' in put_dev_rec:
                    flash('Запись об устройстве была обновлена.', 'correct_rec_dev')
            else:
                flash('Новых изменений не было получено.', 'correct_rec_dev')
            return redirect(url_for('devices.device_detail',
                                    url_dev_id=dev_id_to_url(form.original_dict['dev_id'])))
        elif request.method == 'GET':
            for key, val in form.original_dict.items():
                form[key].data = val

        return render_template('devices/correct_rec.html', title='Корректировка записи об устройстве', form=form,
                               rec_dev=rec_for_edit)
    else:
        return redirect(url_for('auth.login'))


@bp.route('/devices/edit_dev/<int:id>', methods=['GET', 'POST'])
def new_rec_dev(id):
    if request.cookies.get('token'):
        all_departments = requests.get(Config.BACKEND_ADDRESS + "/api/v1/department/all",
                                       headers=make_token_headers())
        if all_departments.status_code == 401:
            return token_401("Срок действия Вашего токена истек. Повторите вход.")
        rec_for_edit = requests.get(f'{Config.BACKEND_ADDRESS}/api/v1/devices/{id}',
                                    headers=make_token_headers()).json()
        if 'error' in rec_for_edit:
            if rec_for_edit['error'] == 'Unauthorized':
                return token_401('Срок действия Вашего токена истек. Повторите вход.')
            elif 'message' in rec_for_edit:
                flash(rec_for_edit['message'], 'correct_rec_dev')
                return redirect(url_for('devices.device_correct_rec', id=id))

        form = EditForm(original_dict={'status': rec_for_edit['status'], 'dev_numb': rec_for_edit['dev_numb'],
                                       'department_id': str(rec_for_edit['department_id']),
                                       'owner': rec_for_edit['owner'],
                                       'remark': rec_for_edit['remark'], 'doc_numb': rec_for_edit['doc_numb'],
                                       'dev_id': rec_for_edit['dev_id'], 'dev_type': rec_for_edit['dev_type']})

        form.department_id.choices = [(k, v) for k, v in all_departments.json().items()]

        if request.method == 'POST':  # form.validate_on_submit():
            have_post_fields = False
            for form_name, val in form.original_dict.items():
                if form_name == 'dev_id':
                    continue
                if form[form_name].data != val:
                    have_post_fields = True
                    break

            print(have_post_fields)
            if have_post_fields:
                new_rec_dev = {'id': id, 'status': form.status.data, 'dev_numb': form.dev_numb.data,
                               'department_id': form.department_id.data, 'owner': form.owner.data,
                               'remark': form.remark.data, 'doc_numb': form.doc_numb.data,
                               'dev_id': form.original_dict['dev_id'], 'dev_type': form.dev_type.data}
                post_dev_rec = requests.post(f'{Config.BACKEND_ADDRESS}/api/v1/devices/new_rec_dev',
                                             data=json.dumps(new_rec_dev, ensure_ascii=False).encode('utf8'),
                                             headers=make_token_headers()).json()
                if 'error' in post_dev_rec:
                    if post_dev_rec['error'] == 'Unauthorized':
                        return token_401(
                            "Данные пользователя не изменены. Срок действия Вашего токена истек. Повторите вход.")
                    elif 'message' in post_dev_rec:
                        flash(post_dev_rec['message'], 'new_rec_dev')
                        return redirect(url_for('devices.new_rec_dev', id=id))
                if 'dev_id' in new_rec_dev:
                    flash('Данные об устройстве изменены (Добавлена новая запись об устройтве).', 'new_rec_dev')
            else:
                flash('Новых изменений не было получено.', 'new_rec_dev')
            return redirect(url_for('devices.device_detail',
                                    url_dev_id=dev_id_to_url(form.original_dict['dev_id'])))
        elif request.method == 'GET':
            for key, val in form.original_dict.items():
                form[key].data = val

        return render_template('devices/edit_dev.html', title='Изменение данных об устройстве', form=form,
                               rec_dev=rec_for_edit)
    else:
        return redirect(url_for('auth.login'))


@bp.route('/devices/add_dev', methods=['POST', 'GET'])
def add_dev():
    if request.cookies.get('token'):
        all_departments = requests.get(Config.BACKEND_ADDRESS + "/api/v1/department/all",
                                       headers=make_token_headers())
        if all_departments.status_code == 401:
            return token_401("Срок действия Вашего токена истек. Повторите вход.")

        form = AddForm()
        form.department_id.choices += [(k, v) for k, v in all_departments.json().items()]

        if form.validate_on_submit():
            new_dev = {'status': form.status.data, 'dev_numb': form.dev_numb.data,
                       'department_id': form.department_id.data, 'owner': form.owner.data,
                       'remark': form.remark.data, 'doc_numb': form.doc_numb.data,
                       'dev_id': form.dev_id.data, 'dev_type': form.dev_type.data}
            post_add_dev = requests.post(f'{Config.BACKEND_ADDRESS}/api/v1/devices/add_dev',
                                         data=json.dumps(new_dev, ensure_ascii=False).encode('utf8'),
                                         headers=make_token_headers()).json()
            if 'error' in post_add_dev:
                if post_add_dev['error'] == 'Unauthorized':
                    return token_401(
                        "Данные пользователя не изменены. Срок действия Вашего токена истек. Повторите вход.")
                elif 'message' in post_add_dev:
                    flash(post_add_dev['message'], 'new_dev')
                    return redirect(url_for('devices.add_dev'))
            if 'dev_id' in post_add_dev:
                flash('Новое устройство добавлено успешно.', 'new_dev')

            return redirect(url_for('devices.devices_all'))

        return render_template('devices/add_device.html', title='Регистрация нового USB-устройства', form=form)
    else:
        return redirect(url_for('auth.login'))


@bp.route('/devices/load_from_file', methods=['POST', 'GET'])
def load_from_file():
    if request.cookies.get('token'):
        report = {}
        if request.method == 'POST':
            # проверим, передается ли в запросе файл
            if 'file' not in request.files:
                # После перенаправления на страницу загрузки
                # покажем сообщение пользователю
                flash('Не могу прочитать файл', 'load_from_file')
                return redirect(url_for('devices.load_from_file'))
            file = request.files['file']
            # Если файл не выбран, то браузер может
            # отправить пустой файл без имени.
            if file.filename == '':
                flash('Нет выбранного файла', 'load_from_file')
                return redirect(url_for('devices.load_from_file'))
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                full_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(full_filename)
                report = requests.post(f'{Config.BACKEND_ADDRESS}/api/v1/devices/load_from_file',
                                       data=json.dumps({'filename': full_filename}, ensure_ascii=False).encode('utf8'),
                                       headers=make_token_headers()).json()
                if 'error' in report:
                    if report['error'] == 'Unauthorized':
                        return token_401(
                            "Данные из файла не были загружены. Срок действия Вашего токена истек. Повторите вход.")
                    else:
                        flash('Операция не выполнена: ' + report['error'], 'load_from_file')
                        return redirect(url_for('devices.load_from_file'))
                elif 'message' in report:
                    flash(report['message'], 'load_from_file')
                    return redirect(url_for('devices.load_from_file'))
                os.remove(full_filename)
            elif not allowed_file(file.filename):
                flash("Неверный формат файла. Укажите файл с раширением .xslsx или .xsls", 'load_from_file')
        return render_template("devices/load_from_file.html", report=report)
    else:
        return redirect(url_for('auth.login'))


def dev_id_to_url(dev_id):
    return dev_id.replace('\\', '*')


def url_to_dev_id(url_dev_id):
    return url_dev_id.replace('*', '\\')


def allowed_file(filename):
    # check file extension
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
