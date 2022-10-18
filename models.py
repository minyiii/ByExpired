from app import db
from utils import dt_converter
from datetime import date, datetime, timedelta, time
from typing import Union

class User(db.Model):
    id = db.Column(db.String(33), primary_key=True, autoincrement=False)
    name = db.Column(db.String(30), nullable=False)
    added_date = db.Column(
        db.DateTime, default=datetime.utcnow()+timedelta(hours=8))
    foods = db.relationship('Food', backref='user')

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return '<User %r>' % self.name

class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    expiration_date = db.Column(db.Date, nullable=False)
    added_date = db.Column(
        db.Date, default=datetime.utcnow()+timedelta(hours=8))
    is_finished = db.Column(db.Boolean(), default=False)
    alarm = db.relationship('Alarm', backref='food', uselist=False) # uselist=False: 1 to 1
    user_id = db.Column(db.String(33), db.ForeignKey('user.id'), nullable=False)

    def __init__(self, name, user_id, expiration_date: Union[str, date]):
        self.name = name
        self.user_id = user_id
        self.expiration_date = expiration_date if isinstance(expiration_date, date) else dt_converter.str_to_date(expiration_date)

    def __repr__(self):
        return '<Food %r>' % self.name

class Alarm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_id =  db.Column(db.Integer, db.ForeignKey('food.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    timing = db.Column(db.Time, nullable=False)
    is_closed = db.Column(db.Boolean(), default=False)

    def __init__(self, start_date: Union[str, date], end_date: Union[str, date], timing: Union[str, time], food_id):
        self.start_date = start_date if isinstance(start_date, date) else dt_converter.str_to_date(start_date)
        self.end_date = end_date if isinstance(end_date, date) else dt_converter.str_to_date(end_date)
        self.timing = timing if isinstance(timing, time) else dt_converter.str_to_time(timing)
        self.food_id = food_id

    def __repr__(self):
        return '<Alarm %r>' % self.timing