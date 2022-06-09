from app.api import bp
from flask import request
import json
from app.models import User, Department
from app import db
from app.api.errors import bad_request


@bp.route('/users/<int:id>', methods=['GET'])
def get_user_by_id(id):
    return json.dumps(User.query.get_or_404(id).to_dict(),
                      ensure_ascii=False).encode('utf8')


@bp.route('/users/<string:username>', methods=['GET'])
def get_user_by_username(username):
    return json.dumps(User.query.filter_by(username=username).first().to_dict(),
                      ensure_ascii=False).encode('utf8')


@bp.route('/users', methods=['GET'])
def get_users():
    pass


@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'username' not in data or 'fullname' not in data or 'password' not in data or 'department_id' not in data:
        return bad_request('must include username, fullname, department and password fields')
    if User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    dep = Department.query.filter_by(name=data['department_id']).first()
    if dep is None:
        return bad_request('wrong name of department. Must be: Отдел_195')
    else:
        data['department_id'] = dep.id

    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = json.dumps(user.to_dict(), ensure_ascii=False).encode('utf8')
    return response


@bp.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    pass


