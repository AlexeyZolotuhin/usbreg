from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, RadioField, widgets
from wtforms.validators import DataRequired, EqualTo


# form for loging user on th site
# checkbox remember_me doesn't use in real form due to
# Username and Password are using just for to get user's token
# and save it in cookie
class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


# Form for registration new user
class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    fullname = StringField('Полное имя', validators=[DataRequired()])
    department = SelectField('Подразделение', choices=[])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password',
                                                                                      message="Пароли не совпадают")])
    submit = SubmitField('Добавить')


# form for edit user's data
class EditUserForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(message="Поле не может быть пустым.")])
    fullname = StringField('Полное имя', validators=[DataRequired(message="Поле не может быть пустым.")])
    department = SelectField('Подразделение', choices=[])
    password = PasswordField('Новый пароль')
    password2 = PasswordField('Повторите пароль', validators=[EqualTo('password', message="Пароли не совпадают")])
    submit = SubmitField('Применить')

    # original_fields are needed for searching data which were changed in form fields
    # in function view when method=POST
    def __init__(self, original_username, original_fullname, original_department_id, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_fullname = original_fullname
        self.original_department_id = original_department_id
