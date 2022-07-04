import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    BACKEND_ADDRESS = "http://127.0.0.1:4000"
    UPLOAD_FOLDER = 'D:\\UsbRegStrela\\load_tmp_files'
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
