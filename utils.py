import json
from datetime import datetime

DATE_FORMAT = '%Y-%m-%d' # Line API 是吃這個時間格式，故不選用其他格式（如：%Y/%m/%d）
TIME_FORMAT = '%H:%M'

class DatetimeConverter:
    def __init__(self, date_format=DATE_FORMAT, time_format=TIME_FORMAT) -> None:
        self.date_format = date_format
        self.time_format = time_format
        
    def str_to_date(self, date_str):
        return datetime.strptime(date_str, self.date_format).date()

    def date_to_str(self, date_obj):
        return date_obj.strftime(self.date_format)

    def str_to_time(self, time_str):
        return datetime.strptime(time_str, self.time_format).time()

    def time_to_str(self, time_obj):
        return time_obj.strftime(self.time_format)

dt_converter = DatetimeConverter()

def get_food_json(food):
    result = json.load(open('single_item.json', 'r', encoding='utf-8'))
    print(type(result))
    result['body']['contents'][0]['text'] = food.name
    result['body']['contents'][2]['contents'][0]['contents'][1]['text'] = dt_converter.date_to_str(food.expiration_date) # to str
    
    if food.alarm:
        print("Have alarm")
        current_alarm = food.alarm
        days_before = abs((current_alarm.end_date - current_alarm.start_date).days)
        alarm_text = f"{dt_converter.time_to_str(current_alarm.timing)} ({str(days_before)} days before)" # to str
    else:
        alarm_text = "No alarm"
        print("No alarm")
    result['body']['contents'][2]['contents'][1]['contents'][1]['text'] = alarm_text

    # 下方按鈕
    result['footer']['contents'][0]['action']['data'] = f"action=edit&food_id={food.id}"
    result['footer']['contents'][1]['action']['data'] = f"action=finished&food_id={food.id}"

    return result

def get_food_jsons(food_list):
    '''
    generate carousel container
    :param food_list: a list of food python objects
    '''
    result = {
        "type": "carousel"
    }
    contents = []
    for food in food_list:
        c = get_food_json(food)
        print(c)
        contents.append(c)
    result["contents"] = contents
    return result

def get_valid_text(text):
    # ref: https://stackoverflow.com/questions/26541968/delete-every-non-utf-8-symbols-from-string
    text = text.encode("utf-8").decode('utf-8','ignore')
    return text

def get_edit_jsons(food):
    result = json.load(open('edit.json', 'r', encoding='utf-8'))
    result['header']['contents'][0]['text'] = f"想改 {food.name} 的什麼呢"

    # 有效期限
    result['body']['contents'][0]['action']['data'] = f"action=setExpDate&food_id={food.id}"
    result['body']['contents'][0]['action']['min'] = dt_converter.date_to_str(datetime.utcnow().date())
    # 開始提醒日
    result['body']['contents'][1]['action']['data'] = f"action=setAlarmStart&food_id={food.id}"
    result['body']['contents'][1]['action']['min'] = dt_converter.date_to_str(datetime.utcnow().date())
    result['body']['contents'][1]['action']['max'] = dt_converter.date_to_str(food.expiration_date)
    # 鬧鐘時間
    result['body']['contents'][2]['action']['data'] = f"action=setAlarmTiming&food_id={food.id}"

    return result