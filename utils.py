import json
from datetime import datetime

def _get_food_json(food):
    result = json.load(open('single_item.json', 'r', encoding='utf-8'))
    print(type(result))
    result['body']['contents'][0]['text'] = food.name
    result['body']['contents'][2]['contents'][0]['contents'][1]['text'] = food.expiration_date.strftime('%Y-%m-%d') # to str
    alarm = food.alarms[0]
    result['body']['contents'][2]['contents'][1]['contents'][1]['text'] = f"{alarm.timing.strftime('%H:%M')} ({str(alarm.days_before)} days before)" # to str
    return result

def _get_food_jsons(food_list):
    '''
    generate carousel container
    :param food_list: a list of food python objects
    '''
    result = {
        "type": "carousel",
        "contents": []
    }
    for food in food_list:
        result["contents"].append(_get_food_json(food))
    return result


def get_food_json(fake_name: str, fake_days_before: int):
    result = json.load(open('single_item.json', 'r', encoding='utf-8'))
    print(type(result))
    result['body']['contents'][0]['text'] = fake_name
    exp_date_obj = datetime.strptime("2022-10-31", '%Y-%m-%d').date()
    alarm_timing_obj = datetime.strptime('17:00', '%H:%M').time()
    alarm_days_before_int = fake_days_before
    result['body']['contents'][2]['contents'][0]['contents'][1]['text'] = exp_date_obj.strftime('%Y-%m-%d')
    result['body']['contents'][2]['contents'][1]['contents'][1]['text'] = f"{alarm_timing_obj.strftime('%H:%M')} ({str(alarm_days_before_int)} days before)"
    return result

def get_food_jsons():
    result = {
        "type": "carousel",
        "contents": []
    }
    for i in range(3):
        result["contents"].append(get_food_json(f"fake {i+1}", f"{i+2}"))
    return result

def get_edit_jsons(fake_food_name):
    result = json.load(open('edit.json', 'r', encoding='utf-8'))
    result['header']['contents'][0]['text'] = f"想改 {fake_food_name} 的什麼呢"
    return result

def _get_edit_jsons(food):
    result = json.load(open('edit.json', 'r', encoding='utf-8'))
    result['header']['contents'][0]['text'] = f"想改 {food.name} 的什麼呢"
    result['body']['contents'][0]['action']['min'] = datetime.utcnow().strftime('%Y-%m-%d') # 有效期限最小僅能當天
    result['body']['contents'][1]['action']['min'] = datetime.utcnow().strftime('%Y-%m-%d') # 開始提醒日最小僅能當天
    result['body']['contents'][1]['action']['max'] = datetime.utcnow().strftime('%Y-%m-%d') # !!開始提醒日最大僅能有效期限當天

    return result