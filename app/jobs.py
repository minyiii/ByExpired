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

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# @scheduler.task('cron', id='do_job_3', day='*', hour='20', minute='20', second='00')
@scheduler.task('cron', id='do_job_3', day='*', hour='*', minute='*', second='30')
def extract_foods_job():
    '''
    extract all foods which need to be reminded and set jobs for them every day
    '''
    with scheduler.app.app_context():
        print("I'm working...")
        foods = read_unfinished_foods_with_alarm()
        print(foods)