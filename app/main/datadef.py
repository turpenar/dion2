from flask_login import UserMixin

from app import db

class User(UserMixin, db.Model):
    """"""
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    character_1 = db.Column(db.PickleType)
    character_2 = db.Column(db.PickleType)
    character_3 = db.Column(db.PickleType)
    character_4 = db.Column(db.PickleType)
    character_5 = db.Column(db.PickleType)
    
db.create_all()
        
    