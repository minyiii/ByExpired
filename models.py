from email.policy import default
from app import db
from datetime import date, datetime, timedelta


class User(db.Model):
    __tablename__ = 'User'
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
    __tablename__ = 'Food'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    expiration_date = db.Column(db.Date, nullable=False)
    added_date = db.Column(
        db.Date, default=datetime.utcnow()+timedelta(hours=8))
    is_finished = db.Column(db.Boolean(), default=False)
    alarms = db.relationship('Alarm', backref='food')
    user_id = db.Column(db.String(33), db.ForeignKey('User.id'), nullable=False)

    def __init__(self, name, user_id, expiration_date):
        self.name = name
        self.user_id = user_id
        self.expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d').date()

    def __repr__(self):
        return '<Food %r>' % self.name

class Alarm(db.Model):
    __tablename__ = 'Alarm'
    id = db.Column(db.Integer, primary_key=True)
    food_id =  db.Column(db.Integer, db.ForeignKey('Food.id'), nullable=False)

    days_before = db.Column(db.Integer, nullable=False)
    timing = db.Column(db.Time, nullable=False)
    is_closed = db.Column(db.Boolean(), default=False)

    def __init__(self, days_before, timing, food_id):
        self.timing = datetime.strptime(timing, '%H:%M').time()
        self.days_before = days_before
        self.food_id = food_id

    def __repr__(self):
        return '<Alarm %r>' % self.timing