from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, RadioField, widgets
from wtforms.validators import ValidationError, DataRequired, EqualTo
from app.models import User, Department
from app.usbparam import status_types_forms, radiofield_filter


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):

    username = StringField('Имя пользователя', validators=[DataRequired()])
    fullname = StringField('Полное имя', validators=[DataRequired()])
    department = SelectField('Подразделение', choices=[])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Добавить')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Пользователь с таким именем уже существует.')


class FilterForm(FlaskForm):
    dev_numb = StringField('По номеру устройства')
    department = SelectField('По подразделению', choices=[(None, "По подразделению")], default=None)
    dev_id = StringField('По идентификатору')
    doc_numb = StringField('По номеру устройства')
    status = SelectField('По статусу', choices=status_types_forms, default=None)
    owner = StringField('По ответственному')
    sortradio = RadioField('Сортировать', choices=radiofield_filter, default="rec_date")
    submit_apply = SubmitField('Применить')
    submit_clear = SubmitField('Очистить')