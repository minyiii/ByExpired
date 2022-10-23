from app import scheduler, Session
from app.crud import read_unfinished_foods_with_alarm
from app.api import send_alarm_message

@scheduler.task('cron', id='extract_foods', hour='12', minute='8')
def extract_foods_job():
    '''
    extract all foods which need to be reminded and set jobs for them every day
    '''
    print("In job!")
    with scheduler.app.app_context():
        with Session() as session:
            try:
                foods = read_unfinished_foods_with_alarm(session)
            except Exception as e:
                print(e)
                session.rollback()
            else:
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
                        func = __name__+':'+job['func'],
                        id = job['id'], 
                        trigger = 'cron', hour = alram_timing.hour, minute = alram_timing.minute, 
                        kwargs = job['kwargs'])

                    print(result)
            finally:
                session.close()