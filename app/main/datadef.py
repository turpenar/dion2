from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String, PickleType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

engine = create_engine('sqlite:///users.db', echo=True)
Base = declarative_base()

class User(Base):
    """"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    character_1 = Column(PickleType)
    character_2 = Column(PickleType)
    character_3 = Column(PickleType)
    character_4 = Column(PickleType)
    character_5 = Column(PickleType)
    
    def __init__(self, username, password):
        """"""
        self.username = username
        self.password = password
        
Base.metadata.create_all(engine)
        
    