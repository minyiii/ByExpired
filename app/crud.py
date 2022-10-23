'''
Access and operate on DB
'''
from app import db
from app.utils import dt_converter
from app.models import User, Food, Alarm
from typing import List, Union

def update_food_exp_date(food_id, exp_date: str, session):
    food = session.execute(db.select(Food).filter_by(id=food_id)).scalar_one()
    food.expiration_date = dt_converter.str_to_date(exp_date)
    if (food.alarm is not None) and (food.alarm.end_date>food.expiration_date):
        food.alarm.end_date = food.expiration_date

def create_user(id, name, session):
    user = User(id, name)
    session.add(user)

def create_food(name, user_id, exp_date: str, session):
    food = Food(name, user_id, exp_date)
    session.add(food)

def create_alarm(food_id, timing: str, start_date: str, end_date: str, session):
    food = Alarm(start_date, end_date, timing, food_id)
    session.add(food)

def update_food_status(food_id, session):
    '''
    Only support finished food, not support reactivate foods
    '''
    food =  session.execute(db.select(Food).filter_by(id=food_id)).scalar_one()
    food.is_finished = True
    if food.alarm is not None:
        food.alarm.is_closed = True

def read_user(user_id: str, session):
    user =  session.execute(db.select(User).filter_by(id=user_id)).scalar_one()
    return user

def read_food(food_id: int, session) -> Union[Food, None]:
    food =  session.execute(db.select(Food).filter_by(id=food_id)).scalar_one()
    return food

def read_alarm(alarm_id: int, session) -> Union[Alarm, None]:
    alarm =  session.execute(db.select(Alarm).filter_by(id=alarm_id)).scalar_one()
    return alarm

def read_unfinished_foods(user_id: str, session) -> Union[List, None]:
    # .join(Alarm, Alarm.food_id==Food.id)
    stmt = db.select(Food)\
            .join(User, User.id==Food.user_id)\
            .filter(User.id==user_id)\
            .filter(Food.is_finished==False)\
            .order_by(Food.expiration_date)
    foods = session.execute(stmt).scalars().all()
    return foods

def read_unfinished_foods_with_alarm(session) -> Union[List, None]:
    '''
    get all unifished foods that have set unclosed alarm
    '''
    stmt = db.select(Food)\
            .join(Alarm, Alarm.food_id==Food.id)\
            .filter(Food.is_finished==False)\
            .filter(Alarm.is_closed==False)\
            .order_by(Food.user_id, Food.expiration_date)
    foods = session.execute(stmt).scalars().all()
    return foods

def update_alarm_date(alarm_id, new_date: str, type: int, session):
    '''
    :param new_date: new date to replace
    :param type: 0 for start_date, 1 for end_date
    '''
    alarm =  session.execute(db.select(Alarm).filter_by(id=alarm_id)).scalar_one()
    new_date_obj = dt_converter.str_to_date(new_date)
    if type==0 and new_date_obj<=alarm.end_date:
        alarm.start_date = new_date_obj
    elif type==1 and new_date_obj>=alarm.start_date:
        alarm.end_date = new_date_obj
    else:
        raise

def update_alarm_timing(alarm_id, new_time:str, session):
    alarm =  session.execute(db.select(Alarm).filter_by(id=alarm_id)).scalar_one()
    alarm.timing = dt_converter.str_to_time(new_time)

def update_alarm_status(alarm_id, session):
    alarm =  session.execute(db.select(Alarm).filter_by(id=alarm_id)).scalar_one()
    alarm.is_closed = not alarm.is_closed