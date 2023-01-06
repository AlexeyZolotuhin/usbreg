from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError
from app.usbparam import status_types_forms, radiofield_filter, dev_type

# message will be show if field is not full
message_empty = "Обязательно для заполнения."


# form for filter devices on all devices page
class FilterForm(FlaskForm):
    dev_numb = StringField('По номеру устройства')
    department_id = SelectField('По подразделению', choices=[(None, "По подразделению")], default=None)
    dev_id = StringField('По идентификатору')
    doc_numb = StringField('По с.з.')
    status = SelectField('По статусу', choices=[(None, 'По статусу')] + status_types_forms, default=None)
    owner = StringField('По ответственному')
    sortradio = RadioField('Сортировать', choices=radiofield_filter, default="rec_date")
    submit_apply = SubmitField('Применить')
    submit_clear = SubmitField('Очистить')


# form for edit device and correcting recording about devices
class EditForm(FlaskForm):
    dev_numb = StringField('Имя USB-устройства', validators=[DataRequired(message=message_empty)])
    dev_id = StringField('Идентификатор устройства', validators=[DataRequired(message=message_empty)])
    dev_type = SelectField('Тип устройства', choices=dev_type)
    department_id = SelectField('Подразделение', choices=[])
    owner = StringField('Ответственный', validators=[DataRequired(message=message_empty)])
    doc_numb = StringField('Номер служебной записки', validators=[DataRequired(message=message_empty)])
    status = SelectField('Статус', choices=status_types_forms)
    remark = TextAreaField('Примечание', validators=[Length(min=0, max=140)])
    submit = SubmitField('Применить')

    # original_dict - dictionary for saving original device data
    # needed to comparing with data in fields of form
    def __init__(self, original_dict, *args, **kwargs):
        super(EditForm, self).__init__(*args, **kwargs)
        self.original_dict = original_dict


# form for adding new device
class AddForm(FlaskForm):
    dev_numb = StringField('Имя USB-устройства', validators=[DataRequired(message=message_empty)])
    dev_id = StringField('Идентификатор устройства', validators=[DataRequired(message=message_empty)])
    dev_type = SelectField('Тип устройства', choices=dev_type, default='USBflash',
                           validators=[DataRequired(message=message_empty)])
    department_id = SelectField('Подразделение', choices=[(None, 'Подразделение')], default=None)
    owner = StringField('Ответственный', validators=[DataRequired(message=message_empty)])
    doc_numb = StringField('Номер служебной записки', validators=[DataRequired(message=message_empty)])
    status = SelectField('Cтатус', choices=status_types_forms, default='Активная')
    remark = TextAreaField('Примечание', validators=[Length(min=0, max=140)])
    submit = SubmitField('Добавить')

    # additional validate for department field
    def validate_department_id(self, department_id):
        if department_id.data == 'None':
            raise ValidationError('Не указано подразделение.')
