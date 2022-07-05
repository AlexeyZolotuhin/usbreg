from app.api.v1 import bp
from flask import request
import json
from app.models import User, Department
from app import db
from app.api.v1.errors import bad_request
from app.api.v1.auth import token_auth


# @bp.route('/users/login/', methods=["POST"])
# def handle_login_request():
#     data = request.get_json() or {}
#     # Check data
#     if 'username' not in data or 'password' not in data or 'remember_me' not in data:
#         return bad_request('Must include username and password fields')
#     # Get and check user and password here
#     user = User.query.filter_by(username=data['username']).first()
#     if user is None or not user.check_password(data['password']):
#         return bad_request('Wrong username or password')
#     login_user(user, remember=data['remember_me'])
#     return json.dumps(user.to_dict(), ensure_ascii=False).encode('utf8')


@bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user_by_id(id):
    return json.dumps(User.query.get_or_404(id).to_dict(),
                      ensure_ascii=False).encode('utf8')


@bp.route('/users/<string:username>', methods=['GET'])
@token_auth.login_required
def get_user_by_username(username):
    return json.dumps(User.query.filter_by(username=username).first().to_dict(),
                      ensure_ascii=False).encode('utf8')


@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_users():
    all_users = [user.to_dict() for user in User.query.all()]
    return json.dumps(all_users, ensure_ascii=False).encode('utf8')


@bp.route('/users/create', methods=['POST'])
# @token_auth.login_required
def create_user():
    data = request.get_json(force=True)
    if 'username' not in data or 'fullname' not in data or 'password' not in data or 'department_id' not in data:
        return bad_request('Для регистрации нового пользователя требуются заполнить все поля')
    if User.query.filter_by(username=data['username']).first():
        return bad_request('Пользователь с таким именем уже существует.')
    dep = Department.query.filter_by(id=int(data['department_id'])).first()
    if dep is None:
        return bad_request('Подразделения с таким именем не существует')
    else:
        data['department_id'] = int(data['department_id'])

    user = User()
    user.from_dict(data)
    db.session.add(user)
    db.session.commit()
    response = json.dumps(user.to_dict(), ensure_ascii=False).encode('utf8')
    return response


@bp.route('/users/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json(force=True) or {}
    if 'username' in data and data['username'] != user.username and \
            User.query.filter_by(username=data['username']).first():
        return bad_request('Пользователь с таким именем уже существует.')

    if 'department_id' in data:
        data['department_id'] = int(data['department_id'])
    user.from_dict(data)
    db.session.commit()
    return json.dumps(user.to_dict(), ensure_ascii=False).encode('utf8')


@bp.route('users/delete/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return '', 204
