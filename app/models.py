from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    fullname = db.Column(db.String(64), index=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    password_hash = db.Column(db.String(128))
    dev_rec = db.relationship('Devinfo', backref='author', lazy='dynamic')

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
            'department': self.department.name,
        }
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'fullname', 'department_id']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Devinfo(db.Model):

    id             = db.Column(db.Integer, primary_key=True)
    dev_numb       = db.Column(db.String(20), nullable=False, index=True)
    dev_id         = db.Column(db.String(150), nullable=False)
    dev_type       = db.Column(db.String(30), default="USBflash")
    department_id  = db.Column(db.Integer, db.ForeignKey('department.id'), index=True)
    owner          = db.Column(db.String(255), nullable=False)
    doc_numb       = db.Column(db.String(200))
    doc_ref        = db.Column(db.String(255))
    status         = db.Column(db.String(25), default="Активная", index=True)
    rec_date       = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    remark         = db.Column(db.Text)
    last_state     = db.Column(db.Boolean, default=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return "<Device {}>".format(self.dev_numb)


class Department(db.Model):

    id                = db.Column(db.Integer, primary_key=True)
    name              = db.Column(db.String(15), nullable=False, unique=True, index=True)
    doc_administrator = db.Column(db.String(255))
    devices           = db.relationship('Devinfo', backref='department')
    users             = db.relationship('User', backref='department')
    permit_computers  = db.relationship('Permit_computer', backref='department')

    def __repr__(self):
        return "<Department {}>".format(self.name)


class Permit_computer(db.Model):

    id            = db.Column(db.Integer, primary_key=True)
    comp_name     = db.Column(db.String(15), nullable=False, index=True)
    status        = db.Column(db.String(25), default="Разрешен", index=True)
    last_state    = db.Column(db.Boolean, default=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    rec_date      = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    remark        = db.Column(db.Text)

    def __repr__(self):
        return "<Computer {}>".format(self.comp_name)