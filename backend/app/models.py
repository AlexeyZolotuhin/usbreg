from app import db
import base64
from datetime import datetime, timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    fullname = db.Column(db.String(64), index=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    password_hash = db.Column(db.String(128))
    dev_rec = db.relationship('Devinfo', backref='author', lazy='dynamic')
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        data = {
            'id': self.id,
            'username': self.username,
            'fullname': self.fullname,
            'department_id': self.department_id,
            'department_name': self.department.name,
        }
        return data

    def from_dict(self, data):
        for field in ['username', 'fullname', 'department_id']:
            if field in data:
                setattr(self, field, data[field])
        if 'password' in data:
            self.set_password(data['password'])

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user


class Devinfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dev_numb = db.Column(db.String(20), nullable=False, index=True)
    dev_id = db.Column(db.String(150), nullable=False)
    dev_type = db.Column(db.String(30), default="USBflash")
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), index=True)
    owner = db.Column(db.String(255), nullable=False)
    doc_numb = db.Column(db.String(200))
    doc_ref = db.Column(db.String(255))
    status = db.Column(db.String(25), default="Активная", index=True)
    rec_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    remark = db.Column(db.Text)
    last_state = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return "<Device {}>".format(self.dev_numb)

    def to_dict(self):
        data = {
            'id': self.id,
            'dev_numb': self.dev_numb,
            'dev_id': self.dev_id,
            'dev_type': self.dev_type,
            'department_id': self.department_id,
            'department_name': self.department.name,
            'owner': self.owner,
            'doc_numb': self.doc_numb,
            'status': self.status,
            'rec_date': str(self.rec_date),
            'remark': self.remark,
            'last_state': self.last_state,
        }
        return data

    def from_dict(self, data):
        for field in ['dev_numb', 'dev_id', 'dev_type', 'department_id',
                      'owner', 'doc_numb', 'status', 'remark', 'last_state', 'rec_date']:
            if field in data:
                setattr(self, field, data[field])

    def get_value_field(self, field):
        return getattr(self, field)


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False, unique=True, index=True)
    doc_administrator = db.Column(db.String(255))
    devices = db.relationship('Devinfo', backref='department')
    users = db.relationship('User', backref='department')
    permit_computers = db.relationship('Permit_computer', backref='department')

    def __repr__(self):
        return "<Department {}>".format(self.name)


class Permit_computer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comp_name = db.Column(db.String(15), nullable=False, index=True)
    status = db.Column(db.String(25), default="Разрешен", index=True)
    last_state = db.Column(db.Boolean, default=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    rec_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    remark = db.Column(db.Text)

    def __repr__(self):
        return "<Computer {}>".format(self.comp_name)
