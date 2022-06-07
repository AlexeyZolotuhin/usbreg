import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://remuser:remUser@192.168.224.31/usbstrela'
    SQLALCHEMY_TRACK_MODIFICATIONS = False