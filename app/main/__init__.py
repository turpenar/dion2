from flask import Blueprint

main = Blueprint('main', __name__,
                 template_folder='templates',
                 static_folder='static')

from app.main import routes, events, world

world.load_tiles()