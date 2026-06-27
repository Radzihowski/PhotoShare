from sqlalchemy import Column, Integer, String, Boolean, func, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(56), nullable=False)
    last_name = Column(String(56), nullable=False)
    email = Column(String(256), nullable=False)
    phone = Column(String(24), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    info = Column(Text, nullable=True)
    created_at = Column('created_at', DateTime, default=func.now())
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    user = relationship('User', backref="contacts")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    created_at = Column('created_at', DateTime, default=func.now())
    confirmed = Column(Boolean, default=False)
    avatar = Column(String(255), nullable=True)


