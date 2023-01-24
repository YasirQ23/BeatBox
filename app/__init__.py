import os
import logging
from flask import Flask
from config import Config
from .auth.routes import auth
from .models import db, login
from flask_migrate import Migrate
from flask_moment import Moment
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler
from flask_mail import Mail

app = Flask(__name__)

mail = Mail(app)

app.config.from_object(Config)

app.register_blueprint(auth)

db.init_app(app)
migrate = Migrate(app, db)

moment = Moment(app)

login.init_app(app)
login.login_view = 'auth.login'
login.login_message = 'Please log in to see this page.'
login.login_message_category = 'danger'

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/beatbox.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Beatbox startup')
