
status_types = {'Active': 'Активная', 'Return': 'Сдана', 'Broken': 'Вышла из строя'}

#списки для SelectField
status_types_forms = [('Активная', 'Активная'), ('Сдана', 'Сдана'), ('Вышла из строя', 'Вышла из строя')]
radiofield_filter = [("rec_date", "По дате"), ("department_name", "По подразделению"), ("dev_numb", "По имени устройства")]
dev_type = [('USBflash', 'USBflash'), ('CardReader', 'CardReader'), ('Usb-HDD', 'Usb-HDD')]