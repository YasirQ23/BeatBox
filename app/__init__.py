from flask import Flask
from config import Config
from .auth.routes import auth

from .models import db, login
from flask_migrate import Migrate
from flask_moment import Moment

app = Flask(__name__)

app.config.from_object(Config)

app.register_blueprint(auth)

db.init_app(app)
migrate = Migrate(app, db)

moment = Moment(app)

login.init_app(app)
login.login_view = 'auth.login'
login.login_message = 'Please log in to see this page.'
login.login_message_category = 'danger'

from . import routes