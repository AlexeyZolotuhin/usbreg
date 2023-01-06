import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    BACKEND_ADDRESS = os.environ.get('BACKEND_ADDRESS') or "http://127.0.0.1:4000"
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or f'D:\load_tmp_files'
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
