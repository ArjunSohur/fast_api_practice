from sqlalchemy import Column, Integer, String, Boolean, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, Sequence('users_user_id_seq'), unique=True, nullable=False)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)

class UserInterests(Base):
    __tablename__ = 'user_interests'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    interests = Column(String)