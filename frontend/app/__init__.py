from flask import Flask
from config import Config
from flask_moment import Moment

moment = Moment()

def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)

    moment.init_app(app)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.devices import bp as devices_bp
    app.register_blueprint(devices_bp)

    return app
