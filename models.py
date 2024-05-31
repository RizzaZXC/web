# -*- coding: UTF-8 -*-
from sqlalchemy import Column,  Integer,Float,Date,  DateTime, Text, Boolean, String, ForeignKey, or_, not_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship, query_expression
from sqlalchemy.sql import func
from database import Base, db_session, engine as db_engine
import datetime
from flask_login import UserMixin


class Dishes(Base):
    __tablename__ = 'dish'
    id    = Column(Integer, primary_key=True)
    foodname = Column(String(100), nullable=False, default="")
    fooddescrip = Column(String(1000), nullable=False, default="")
    price = Column(Integer, nullable=False, default=0)
    weight = Column(Integer, nullable=False, default=0)
    dish_id = Column(Integer, ForeignKey('Type.id'), doc="Тип блюда")
    dish = relationship("DishType", back_populates="typemenulist")
    image = Column(String(500), nullable=False, default="")


class DishType(Base):
    __tablename__ = 'Type'
    id    = Column(Integer, primary_key=True)
    typelable = Column(String(100), nullable=False, default="")
    typemenulist = relationship("Dishes", back_populates="dish")


class ReservedTable(Base):
    __tablename__ = 'reservtable'
    id    = Column(Integer, primary_key=True)
    fio = Column(String(100), nullable=False, default="")
    bookdate = Column(DateTime, nullable=False)
    numtable = Column(Integer, nullable=False, default=0)
    orderedfood = Column(String(10000), nullable=False, default="")
    phonnumb = Column(String(10), nullable=False, default="")
    numppl = Column(Integer, nullable=False, default=0)
##    user = relationship('User', back_populates='orders')

class Restoran(Base):
    __tablename__ = 'restorandata'
    id    = Column(Integer, primary_key=True)
    restname = Column(String(100), nullable=False, default="")
    restnumb = Column(String(10), nullable=False, default="")
    emile = Column(String(100), nullable=False, default="")
    adres = Column(String(100), nullable=False, default="")
    workhoursweek = Column(String(100), nullable=False, default="")
    worktime = Column(String(100), nullable=False, default="")

class User(Base, UserMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    mail = Column(String(200),nullable=False, default="")
    login = Column(String(100),unique=True)
    password = Column(String(200))
##  orders = relationship('ReservedTable', back_populates='user')

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from database import engine
    Base.metadata.create_all(bind=engine)
    db_session.commit()

def print_schema(table_class):
    from sqlalchemy.schema import CreateTable, CreateColumn
    print(str(CreateTable(table_class.__table__).compile(db_engine)))

def print_columns(table_class, *attrNames):
   from sqlalchemy.schema import CreateTable, CreateColumn
   c = table_class.__table__.c
   print( ',\r\n'.join((str( CreateColumn(getattr(c, attrName)).compile(db_engine)) \
                            for attrName in attrNames if hasattr(c, attrName)
               )))

if __name__ == "__main__":
    init_db()
    #print_columns(Payment, "created")
    #print_schema(SoltButton)
