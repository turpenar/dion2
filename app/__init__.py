from flask import Flask
from flask_socketio import SocketIO
from flask_wtf import CsrfProtect
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import eventlet

socketio = SocketIO(async_mode="eventlet")
csrf = CsrfProtect()
eventlet.monkey_patch()
login_manager = LoginManager()
db = SQLAlchemy()

def create_app(debug=True):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'Dion'
    app.config['DEBUG'] = debug
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main/users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    db.init_app(app)
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    socketio.init_app(app)
    return app

