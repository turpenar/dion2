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
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
        
    