import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    BACKEND_ADDRESS = os.environ.get('BACKEND_ADDRESS')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
