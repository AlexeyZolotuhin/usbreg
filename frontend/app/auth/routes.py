from flask import render_template, make_response, url_for, request, flash, redirect
from app import Config
from app.auth import bp
from app.token import token_401, make_token_headers
from app.auth.forms import LoginForm, RegistrationForm, EditUserForm
import requests
from requests.auth import HTTPBasicAuth
import json


# Function view of auth page
@bp.route('/login', methods=['GET', 'POST'])
def login():
    # create obj of form for auth
    form = LoginForm()
    # check: is there token in user's browser cookie?
    # yes - go to page of all devices. There will be verification token alive or not
    if request.cookies.get('token'):
        return redirect(url_for('devices.devices_all'))
    # check push the button in form. POST request.
    if form.validate_on_submit():
        # request for token from backend with pointed username and password
        token = requests.post(Config.BACKEND_ADDRESS + "/api/v1/tokens",
                              auth=HTTPBasicAuth(form.username.data, form.password.data))
        # check answer. If answer is wrong add message in flash with category error_loging
        # 401 - error of auth, in this case go to login page and show message from flash
        if token.status_code == 401:
            flash('Неверное имя пользователя или пароль', 'error_login')
            return render_template('auth/login.html', title='Войти', form=form)
        # make response - add username and token in cookie, and go to all devices page
        res = make_response('', 301)
        res.headers['Location'] = url_for('devices.devices_all')
        res.set_cookie('token', token.json()['token'])
        res.set_cookie('username', form.username.data)
        return res
    # if GET just render login page
    return render_template('auth/login.html', title='Войти', form=form)


# function view of logout
@bp.route('/logout')
def logout():
    # token_401(msg) - usually using when some request gets error 401 (error auth), in general that means token is dead.
    # msg - message will be show on login page
    # In this case clearing cookie and go to login page.
    # But is same that logout
    return token_401("Произведен выход")


# function view of register new user
@bp.route('/register', methods=['GET', 'POST'])
def register():
    # check token in cookie
    if request.cookies.get('token'):
        # create form for registration of new user
        form = RegistrationForm()
        # request for all departments on backend
        all_departments = requests.get(Config.BACKEND_ADDRESS + "/api/v1/department/all", headers=make_token_headers())
        # check token is alive or not
        if all_departments.status_code == 401:
            return token_401("Срок действия Вашего токена истек. Повторите вход.")
        # full select field form of departments by received data:
        # k - id of department in BD. This value will be sent to backend for add new user
        # v - name of department
        form.department.choices = [(k, v) for k, v in all_departments.json().items()]
        # process POST
        if form.validate_on_submit():
            # create dict with new user's data from form
            new_user = {'username': form.username.data, 'fullname': form.fullname.data,
                        'department_id': form.department.data, 'password': form.password.data}
            # make request for adding new user
            # make_token_headers() - this func add in headers token from cookie
            created_user = requests.post(url=Config.BACKEND_ADDRESS + "/api/v1/users/create",
                                         data=json.dumps(new_user), headers=make_token_headers()).json()
            # check what we get in created_user
            if 'error' in created_user:
                # 401 code error. Our token is dead
                if created_user['error'] == 'Unauthorized':
                    return token_401(
                        "Новый пользователь не добавлен. Срок действия Вашего токена истек. Повторите вход.")
                # if other error which we didn't expect - create flash mes with category create_user
                # and refresh page with flash mes
                else:
                    flash('Операция не выполнена: ' + created_user['error'], 'create_user')
                    return redirect(url_for('auth.register'))
            # if get some message from backend instead user's data
            elif 'message' in created_user:
                flash(created_user['message'], 'create_user')
                return redirect(url_for('auth.register'))
            # in successful result we get user's data with username etc
            # in this case just add flash mes
            if 'username' in created_user:
                flash(f"Новый пользователь {created_user['username']} добавлен!", 'create_user')
        return render_template('auth/register.html', title='Добавить пользователя', form=form)

    else:
        # didn't find token in  the client's cookie - go login page
        return redirect(url_for('auth.login'))


# func view for all users list
# here we can see all users and have href to edit user page and delete user
@bp.route('/uses')
def get_all_users():
    # again check token in cookie. Yes, we like cookie. Yum Yum Yum
    if request.cookies.get('token'):
        # make request for all users
        all_users = requests.get(Config.BACKEND_ADDRESS + '/api/v1/users', headers=make_token_headers()).json()
        # check what in all_users
        if 'error' in all_users:
            # 401 code error. Our token is dead
            if all_users['error'] == 'Unauthorized':
                return token_401(
                    "Срок действия Вашего токена истек. Повторите вход.")
            # if other error which we didn't expect - create flash mes with category get_all_user
            # and refresh page with flash mes
            else:
                flash('Операция не выполнена: ' + all_users['error'], 'get_all_user')
                return redirect(url_for('auth.get_all_users'))
        elif 'message' in all_users:
            flash(all_users['message'], 'get_all_user')
            return redirect(url_for('auth.get_all_users'))

        return render_template('auth/users.html', title='Список зарегистрированных пользователей', users=all_users)
    else:
        # didn't find token in  the client's cookie - go login page
        return redirect(url_for('auth.login'))


# func deleting user
# id - user's id in user's table
@bp.route('/users/delete/<int:id>')
def delete_user(id):
    # check token in cookie
    if request.cookies.get('token'):
        # make DELETE request of user
        # make_token_headers() - add token in headers
        deleted_user = requests.delete(f'{Config.BACKEND_ADDRESS}/api/v1/users/delete/{id}',
                                       headers=make_token_headers())
        # check result of request
        # in this case didn't use json()-method for deleted_user
        # and check directly status code in result
        if deleted_user.status_code == 204:
            flash(f'Пользователь удален успешно', 'users_list')
            return redirect(url_for('auth.get_all_users'))
        elif deleted_user.status_code == 401:
            return token_401("Срок действия Вашего токена истек. Пользователь не удален.")
        else:
            flash(f'При удалении пользователя произошла ошибка: {deleted_user.status_code}', 'users_list')
            return redirect(url_for('auth.get_all_users'))
    else:
        # didn't find token in  the client's cookie - go login page
        return redirect(url_for('auth.login'))


# func view for edit user page
# id - user's id in user's table
@bp.route('users/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    # try to find token in cookie
    if request.cookies.get('token'):
        # get id and name of all departments for select field form
        all_departments = requests.get(Config.BACKEND_ADDRESS + "/api/v1/department/all", headers=make_token_headers())
        # check answer by status code
        if all_departments.status_code == 401:
            return token_401("Срок действия Вашего токена истек. Повторите вход.")
        # get data of user by id
        user_for_edit = requests.get(f'{Config.BACKEND_ADDRESS}/api/v1/users/{id}', headers=make_token_headers()).json()
        # check result
        # do I need to create a separate func for it? I tried - bad result.
        if 'error' in user_for_edit:
            # 401 code error. Our token is dead
            if user_for_edit['error'] == 'Unauthorized':
                return token_401(
                    "Срок действия Вашего токена истек. Повторите вход.")
            # if other error which we didn't expect - create flash mes with category edit_user
            # and refresh page with flash mes
            else:
                flash('Операция не выполнена: ' + user_for_edit['error'], 'edit_user')
                return redirect(url_for('auth.get_all_users'))
        elif 'message' in user_for_edit:
            flash(user_for_edit['message'], 'edit_user')
            return redirect(url_for('auth.get_all_users'))
        # create form obj for edit user
        # args of form - original user data
        form = EditUserForm(user_for_edit['username'], user_for_edit['fullname'],
                            user_for_edit['department_id'])
        # full select field form of departments by received departments data:
        # k - id of department in BD. This value will be sent to backend for add new user
        # v - name of department
        form.department.choices = [(k, v) for k, v in all_departments.json().items()]

        # POST
        if form.validate_on_submit():
            # changed_fields - dictionary for saving changed data
            changed_fields = {}
            # searching data which were changed and append them in changed_fields
            if form.username.data != form.original_username:
                changed_fields['username'] = form.username.data
            if form.fullname.data != form.original_fullname:
                changed_fields['fullname'] = form.fullname.data
            if form.department.data != str(form.original_department_id):
                changed_fields['department_id'] = form.department.data
            if form.password.data:
                changed_fields['password'] = form.password.data
            # if we found some changed data
            if len(changed_fields) != 0:
                # make PUT request for change user's data
                put_user = requests.put(f'{Config.BACKEND_ADDRESS}/api/v1/users/{id}',
                                        data=json.dumps(changed_fields, ensure_ascii=False).encode('utf8'),
                                        headers=make_token_headers()).json()
                # check result
                if 'error' in put_user:
                    # 401 code error. Our token is dead
                    if put_user['error'] == 'Unauthorized':
                        return token_401(
                            "Срок действия Вашего токена истек. Повторите вход.")
                    # if other error which we didn't expect - create flash mes with category edit_user
                    # and refresh page with flash mes
                    else:
                        flash('Операция не выполнена: ' + put_user['error'], 'edit_user')
                        return redirect(url_for('auth.edit_user', id=id))
                elif 'message' in put_user:
                    flash(put_user['message'], 'edit_user')
                    return redirect(url_for('auth.edit_user', id=id))
                # if all is ok we have username in put_user
                if 'username' in put_user:
                    flash('Данные пользователя были успешно изменены.', 'edit_user')
        else:
            # nothing was changed
            flash('Новых изменений данных пользователя не было получено.', 'edit_user')
            return redirect(url_for('auth.get_all_users'))

        return render_template('auth/edit_user.html', title='Редактирование пользователя', form=form,
                               user=user_for_edit)
    else:
        return redirect(url_for('auth.login'))
