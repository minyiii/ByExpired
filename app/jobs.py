'''
1. 取得所有未吃完且有鬧鐘的食物
2. 以用戶分類
3. 提醒各用戶他的XX食物期限在X天後
    - 格式
        哈囉{user_name}，你的
        - {food} 即將在 {str(exp_date-today)} 天後 ({exp_date}) 過期
        - {food} 即將在 {str(exp_date-today)} 天後 ({exp_date}) 過期
        記得在過期前吃掉ㄛ！
'''
from flask_apscheduler import APScheduler
from app import app
from app.crud import read_unfinished_foods_with_alarm
from app.api import send_alarm_message

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# @scheduler.task('cron', id='extract_foods', day='*', hour='20', minute='20', second='00')
@scheduler.task('cron', id='extract_foods', day='*', hour='*', minute='52', second='0')
def extract_foods_job():
    '''
    extract all foods which need to be reminded and set jobs for them every day
    '''
    with scheduler.app.app_context():
        foods = read_unfinished_foods_with_alarm()
        for food in foods:
            job = {  
                'id': f'job_{food.id}',  # job的unique id
                'func':'send_alarm_message', # 執行任務的function名稱
                'kwargs': {  # 要傳入function的參數
                    'user_id': food.user_id,
                    'food_name': food.name,
                    'food_exp_date': food.expiration_date
                }
            }
            alram_timing = food.alarm.timing
            result = scheduler.add_job(
                func=__name__+':'+job['func'],
                id=job['id'], 
                trigger='cron', hour=alram_timing.hour, minute=alram_timing.minute, 
                kwargs = job['kwargs'])

            print(result)