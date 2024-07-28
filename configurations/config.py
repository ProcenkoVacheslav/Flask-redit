from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import Flask

DEBUG = True
SECRET_KEY = 'asdsa34543fjkb@h33k566786as@cavsx345acv34sc'
POSTS_PER_PAGE = 20

app = Flask(__name__)
app.config.from_object(__name__)

app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.login_message = 'Вы не авторизованы, пожалуйста авторизуйтесь.'
login_manager.login_message_category = 'light_error'
