import eventlet
eventlet.monkey_patch()

from flask import Flask
from flask_wtf.csrf import CsrfProtect
from flask_login import LoginManager
from flask_session import Session
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


csrf = CsrfProtect()
login_manager = LoginManager()
session = Session()
socketio = SocketIO()
db = SQLAlchemy()
migrate = Migrate()



def create_app(debug=True):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'Your Kung-Fu is Very Good'
    app.config['DEBUG'] = debug
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main/users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_PERMANENT'] = True
    app.config['SESSION_TYPE'] = "sqlalchemy"
    app.config['SESSION_SQLALCHEMY_TABLE'] = "users"
    app.config['SESSION_SQLALCHEMY'] = db
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    socketio.init_app(app, async_mode='eventlet', manage_session=False)
    session.init_app(app)
    migrate.init_app(app, db)
    with app.app_context():
        from app.main import main as main_blueprint
        app.register_blueprint(main_blueprint)
        db.create_all()
        return app

