from flask import Flask
from flask_socketio import SocketIO
from flask_wtf.csrf import CsrfProtect

socketio = SocketIO()
csrf = CsrfProtect()

def create_app(debug=True):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'Dion'
    app.config['DEBUG'] = debug
    csrf.init_app(app)
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    socketio.init_app(app)
    return app