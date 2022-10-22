'''
Access and operate on DB
'''
from app import db
from app.utils import dt_converter
from app.models import User, Food, Alarm
from typing import List, Union

def update_food_exp_date(food_id, exp_date: str):
    food =  db.session.execute(db.select(Food).filter_by(id=food_id)).scalar_one()
    food.expiration_date = dt_converter.str_to_date(exp_date)
    if (food.alarm is not None) and (food.alarm.end_date>food.expiration_date):
        food.alarm.end_date = food.expiration_date

def add_food(name, user_id, exp_date: str):
    food = Food(name, user_id, exp_date)
    db.session.add(food)

def add_alarm(food_id, timing: str, start_date: str, end_date: str):
    food = Alarm(start_date, end_date, timing, food_id)
    db.session.add(food)

def update_food_status(food_id):
    '''
    Only support finished food, not support reactivate foods
    '''
    food =  db.session.execute(db.select(Food).filter_by(id=food_id)).scalar_one()
    food.is_finished = True
    if food.alarm is not None:
        food.alarm.is_closed = True

def read_food(food_id: int) -> Union[Food, None]:
    food =  db.session.execute(db.select(Food).filter_by(id=food_id)).scalar_one()
    return food

def read_alarm(alarm_id: int) -> Union[Alarm, None]:
    alarm =  db.session.execute(db.select(Alarm).filter_by(id=alarm_id)).scalar_one()
    return alarm

def read_unfinished_foods(user_id: str) -> Union[List, None]:
    # .join(Alarm, Alarm.food_id==Food.id)
    stmt = db.select(Food)\
            .join(User, User.id==Food.user_id)\
            .filter(User.id==user_id)\
            .filter(Food.is_finished==False)\
            .order_by(Food.expiration_date)
    foods = db.session.execute(stmt).scalars().all()
    return foods

def read_unfinished_foods_with_alarm() -> Union[List, None]:
    '''
    get all unifished foods that have set unclosed alarm
    '''
    stmt = db.select(Food)\
            .join(Alarm, Alarm.food_id==Food.id)\
            .filter(Food.is_finished==False)\
            .filter(Alarm.is_closed==False)\
            .order_by(User.id, Food.expiration_date)
    foods = db.session.execute(stmt).scalars().all()
    return foods

def update_alarm_date(alarm_id, new_date: str, type: int):
    '''
    :param new_date: new date to replace
    :param type: 0 for start_date, 1 for end_date
    '''
    alarm =  db.session.execute(db.select(Alarm).filter_by(id=alarm_id)).scalar_one()
    new_date_obj = dt_converter.str_to_date(new_date)
    if type==0 and new_date_obj<=alarm.end_date:
        alarm.start_date = new_date_obj
    elif type==1 and new_date_obj>=alarm.start_date:
        alarm.end_date = new_date_obj
    else:
        raise

def update_alarm_timing(alarm_id, new_time:str):
    alarm =  db.session.execute(db.select(Alarm).filter_by(id=alarm_id)).scalar_one()
    alarm.timing = dt_converter.str_to_time(new_time)

def update_alarm_status(alarm_id):
    alarm =  db.session.execute(db.select(Alarm).filter_by(id=alarm_id)).scalar_one()
    alarm.is_closed = not alarm.is_closed

def _update_food_alarm(food_id, start_date):
    food = read_food(food_id)
    if food.alarm is None:
        update_alarm_date(food.alarm.id, start_date, type=0)
    else:
        add_alarm(food_id, timing="08:00", start_date=start_date, end_date=food.expiration_date)

# -------------------------------

def create_object(new_object: Union[User, Food, Alarm]) -> bool:
    db.session.add(new_object)
    # # 
    # try:
    #     if not isinstance(new_object, (User, Food, Alarm)):
    #         raise TypeError
    #     db.session.add(new_object)
    # except TypeError as e:
    #     print(f"無法新增物件，請傳入正確的物件型態")
    # except Exception as e:
    #     print(f"無法新增物件，發生 {str(e)} 錯誤")
    #     db.session.rollback()
    #     return False
    # else:
    #     db.session.commit()
    #     return True

def create_objects(new_objects: List[Union[User, Food, Alarm]]) -> bool:
    try:
        if not (
            isinstance(new_objects, list) and 
            all(isinstance(new_object, (User, Food, Alarm)) for new_object in new_objects)):
                raise TypeError # 不會執行，直接去except
        db.session.add_all(new_objects)
    except TypeError as e:
        print(f"無法新增物件，請傳入正確的物件型態")
        return False
    except Exception as e:
        print(f"無法新增物件們，發生 {str(e)} 錯誤")
        db.session.rollback()
        return False
    else:
        db.session.commit()
        return True

def read_user_by_id(user_id: str) -> Union[bool, None]:
    try:
        user =  db.session.execute(db.select(User).filter_by(id=user_id)).scalar_one()
    except Exception as e:
        print(f"無法新增讀取用戶，發生 {str(e)} 錯誤")
        db.session.rollback()
        return None
    else:
        return user

def update_object() -> bool:
    '''
    No matter what object to be updated, same operations (commit) to be executed.
    '''
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"無法更新資料，發生 {str(e)} 錯誤")
        return False
    else:
        return True

def read_unfinished_foods_by_user_id(user_id: str) -> Union[List, None]:
    stmt = db.select(Food)\
            .join(User, User.id==Food.user_id)\
            .join(Alarm, Alarm.food_id==Food.id)\
            .filter(User.id==user_id)\
            .filter(Food.is_finished==False)\
            .order_by(Food.expiration_date)
    # print(stmt)
    try:
        foods = db.session.execute(stmt).scalars().all()
    except Exception as e:
        print(f"無法讀取此用戶(id={user_id})的食物，發生 {str(e)} 錯誤")
        db.session.rollback()
        return None
    else:
        return foods

def read_food_by_food_id(food_id) -> Union[Food, None]:
    try:
        food =  db.session.execute(db.select(Food).filter_by(id=food_id)).scalar_one()
    except Exception as e:
        print(f"無法讀取id={food_id}之食物，發生 {str(e)} 錯誤")
        db.session.rollback()
        return None
    else:
        return food