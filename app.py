from datetime import datetime
import os
import sys
import json
from argparse import ArgumentParser
from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (MessageEvent, PostbackEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, 
MessageAction, DatetimePickerAction, FlexSendMessage, TemplateSendMessage, ConfirmTemplate, PostbackAction)
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI')
db = SQLAlchemy(app)

from models import User, Alarm, Food # must keep this to create table
from utils import get_valid_text, dt_converter, get_food_jsons, get_edit_jsons
import crud

channel_access_token = os.getenv('CHANNEL_ACCESS_TOKEN')
channel_secret = os.getenv('CHANNEL_SECRET')

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


@app.teardown_appcontext
def shutdown_session(exception=None):
    ''' Enable Flask to automatically remove DB sessions 
    at the end of the request or when the application shuts down.
    Ref: http://flask.pocoo.org/docs/patterns/sqlalchemy/
    '''
    print("remove!!!!!!!!!!!")
    db.session.remove()

# 所有line傳來的事件都會經過此路徑，接著將事件傳到下方的handler做處理

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        profile = line_bot_api.get_profile(event.source.user_id)
    except LineBotApiError as e:
        print("No profile.")

    option_text = event.message.text
    if option_text == "查看品項": # OK
        try:
            foods = crud.read_unfinished_foods(user_id = event.source.user_id)
            print(foods)
        except:
            db.session.rollback()
            line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="查看食物失敗"))
        else:
            if len(foods)!=0:
                print(foods)
                content = get_food_jsons(foods)
                with open("read_food.json", "w") as outfile:
                    json.dump(content, outfile)
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text = '這些是你目前的食物呦',
                        contents = content
                    )
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你目前沒任何食物喔"))
            
    elif option_text.startswith("取消"):
        pass
    elif option_text[0]=="+":
        food_name = get_valid_text(option_text[1:])
        confirm_msg = TemplateSendMessage(
            alt_text = "新增品項", 
            template = ConfirmTemplate(
                text = f"你要新增 {food_name} 對嗎",
                actions = [
                    DatetimePickerAction(
                        label= "選擇有效期限", 
                        data = "action=addFood&name={}".format(food_name), 
                        min = dt_converter.date_to_str(datetime.utcnow().date()),
                        mode = "date"),
                    MessageAction(
                        label='取消',
                        text=f'取消新增{food_name}'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, confirm_msg)

    else:
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"嗨！{profile.display_name}，若要新增食物請以「+食物名」的格式哦（例如：+鮪魚罐頭），並切勿輸入表情符號！！"))
    '''elif option_text == "怕忘記":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text="幾天前開始提醒？",
                quick_reply = QuickReply(
                    items=[
                        QuickReplyButton(action=MessageAction(label="1", text="1 天前開始提醒")),
                        QuickReplyButton(action=MessageAction(label="2", text="2 天前開始提醒")),
                        QuickReplyButton(action=MessageAction(label="3", text="3 天前開始提醒")),
                        QuickReplyButton(action=MessageAction(label="4", text="4 天前開始提醒")),
                        QuickReplyButton(action=MessageAction(label="5", text="5 天前開始提醒")),
                        QuickReplyButton(action=DatetimePickerAction(
                            label="請輸入過期日", data =f"mode=date&userId={event.source.user_id}&itemId=5", mode ="date")),
                        QuickReplyButton(action=DatetimePickerAction(
                            label="請輸入鬧鐘", data =f"type=time&userId={event.source.user_id}&itemId=7", mode ="time"))
                    ]
                )
            )
        )'''

@handler.add(PostbackEvent)
def handle_postback(event):
    action, pb_data = event.postback.data.split("&", 1)
    action = action.split("=")[1]

    if action == "edit": # OK
        food_id = int(pb_data.split("&")[0].split("=")[1])
        try:
            food = crud.read_food(food_id=food_id)
        except:
            db.session.rollback()
            line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="編輯食物失敗"))
        else:
            content = get_edit_jsons(food)
            with open("test.json", "w") as outfile:
                json.dump(content, outfile)
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text = '請進行編輯',
                    contents = content
                )
            )
    elif action == "setExpDate": # OK
        new_exp_date = event.postback.params['date']
        food_id = int(pb_data.split("=")[1])
        
        try:
            crud.update_food_exp_date(food_id, new_exp_date)
            db.session.commit()
        except:
            text = "有效期限修改失敗"
            db.session.rollback()
            raise
        else:
            text =f"有效期限已改為 {new_exp_date}"
        finally:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=text))
    elif action == "setAlarmStart": # OK
        new_start_date = event.postback.params['date']
        alarm, food = pb_data.split("&")
        alarm_id = int(alarm.split("=")[1])
        food_id = int(food.split("=")[1])
        
        try:
            food = crud.read_food(food_id)
            print(f"food.alarm: {food.alarm}")
            if food.alarm is not None:
                crud.update_alarm_date(alarm_id, new_start_date, type=0)
            else:
                crud.add_alarm(food_id, timing = "08:00", 
                    start_date = new_start_date, 
                    end_date = food.expiration_date)
            db.session.commit()
        except:
            text = "鬧鐘開始提醒日修改失敗"
        else:
            text = f"鬧鐘開始提醒日已改為 {new_start_date}"
        finally:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=text))
        '''line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text="幾天前開始提醒？",
                quick_reply = QuickReply(
                    items=[
                        QuickReplyButton(action=MessageAction(label="1", text="1 天前開始提醒")),
                        QuickReplyButton(action=MessageAction(label="2", text="2 天前開始提醒")),
                        QuickReplyButton(action=MessageAction(label="3", text="3 天前開始提醒")),
                        QuickReplyButton(action=MessageAction(label="4", text="4 天前開始提醒")),
                        QuickReplyButton(action=MessageAction(label="5", text="5 天前開始提醒")),
                    ]
                )
            )
        )'''
    elif action == "setAlarmTiming": # OK
        new_time = event.postback.params['time']
        alarm, food = pb_data.split("&")
        alarm_id = int(alarm.split("=")[1])
        food_id = int(food.split("=")[1])
        print(f"alarm_id: {alarm_id}, food_id: {food_id}")

        try:
            food = crud.read_food(food_id)
            print(f"food.alarm: {food.alarm}")
            if food.alarm is not None:
                print("(1) food.alarm is not None")
                crud.update_alarm_timing(
                    alarm_id = alarm_id, 
                    new_time = new_time)
            else:
                print("(2) food.alarm is None")
                crud.add_alarm(food_id, timing = new_time, 
                        start_date = datetime.utcnow().date(), 
                        end_date = food.expiration_date)
            db.session.commit()
        except:
            text = "鬧鐘提醒時間修改失敗"
        else:
            text = f"鬧鐘提醒時間已改為 {new_time}"
        finally:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=text))

    elif action == "addFood": # OK
        food_name = pb_data.split("=")[1]
        exp_date = event.postback.params['date']
        
        try:
            crud.add_food(
                name = food_name, 
                user_id = event.source.user_id,
                exp_date = exp_date)
            db.session.commit()
        except:
            text = "新增食物失敗"
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=text))
        else:
            text = f"已新增 {exp_date} 過期的{food_name}"

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text=f"{text} $",
                    emojis = [
                        {
                            "index": len(text)+1,
                            "productId": "5ac21a18040ab15980c9b43e",
                            "emojiId": "006"
                        }
                    ]
                ))

    elif action == "finished": # OK
        food_id = int(pb_data.split("=")[1])
        try:
            crud.update_food_status(food_id = food_id)
            db.session.commit()
        except:
            text = "吃完食物失敗"
        else:
            text = "已吃完！"
        finally:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=text))

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    # --- original code ---
    # arg_parser.add_argument('-p', '--port', type=int, default=8000, help='port')
    # arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    # options = arg_parser.parse_args()
    # app.run(debug=options.debug, port=options.port)

    # --- new code ---
    http_port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=http_port)
