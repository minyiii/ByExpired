'''
Line bot API
'''
import os
import sys
from datetime import datetime

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import LineBotApiError
from linebot.models import (MessageEvent, PostbackEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, 
MessageAction, DatetimePickerAction, FlexSendMessage, TemplateSendMessage, ConfirmTemplate, PostbackAction)

from app import db, Session
from app.utils import get_valid_text, dt_converter, get_food_jsons, get_edit_jsons
from app import crud

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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        profile = line_bot_api.get_profile(event.source.user_id)
    except LineBotApiError as e:
        print("No profile.")

    option_text = event.message.text
    if option_text == "查看品項": # OK
        with Session() as session:
            try:
                foods = crud.read_unfinished_foods(
                    user_id = event.source.user_id, 
                    session = session)
                print(foods)
            except Exception as e:
                print(e)
                session.rollback()
                line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="查看食物失敗"))
            else:
                if len(foods)!=0:
                    print(foods)
                    content = get_food_jsons(foods)
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
            finally:
                session.close()
            
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
        food_id = int(pb_data.split("=")[1])
        with Session() as session:
            try:
                food = crud.read_food(food_id=food_id, session=session)
                print(f"Are these session the same? {session==db.session}")
                print(f"session: {session}")
                print(f"db.session: {db.session}")
            except Exception as e:
                print(e)
                session.rollback()
                line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="編輯食物失敗"))
            else:
                content = get_edit_jsons(food)
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text = '請進行編輯',
                        contents = content
                    )
                )
            finally:
                session.close()
    elif action == "setExpDate": # OK
        new_exp_date = event.postback.params['date']
        food_id = int(pb_data.split("=")[1])
        with Session() as session:
            try:
                crud.update_food_exp_date(food_id, new_exp_date, session)
                session.commit()
            except Exception as e:
                print(e)
                text = "有效期限修改失敗"
                session.rollback()
                raise
            else:
                text =f"有效期限已改為 {new_exp_date}"
            finally:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=text))
                session.close()
    elif action == "setAlarmStart": # OK
        new_start_date = event.postback.params['date']
        food_id = int(pb_data.split("=")[1])
        with Session() as session:
            try:
                food = crud.read_food(food_id, session = session)
                print(f"food.alarm: {food.alarm}")
                if food.alarm is not None:
                    print(f"food_id.alarm.id: {food.alarm.id}, new_start_date: {new_start_date}")
                    crud.update_alarm_date(food.alarm.id, 
                        new_start_date, type=0, session = session)
                else:
                    print("根本沒鬧鐘")
                    crud.add_alarm(food_id, timing = "08:00", 
                        start_date = new_start_date, 
                        end_date = food.expiration_date,
                        session=session)
                session.commit()
            except Exception as e:
                print(e)
                text = "鬧鐘開始提醒日修改失敗"
                session.rollback()
            else:
                text = f"鬧鐘開始提醒日已改為 {new_start_date}"
            finally:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=text))
                session.close()
    elif action == "setAlarmTiming": # OK
        new_time = event.postback.params['time']
        food_id = int(pb_data.split("=")[1])
        with Session() as session:
            try:
                food = crud.read_food(food_id, session = session)
                print(f"food.alarm: {food.alarm}")
                if food.alarm is not None:
                    print("(1) food.alarm is not None")
                    crud.update_alarm_timing(
                        alarm_id = food.alarm.id, 
                        new_time = new_time,
                        session = session)
                else:
                    print("(2) food.alarm is None")
                    crud.add_alarm(food_id, timing = new_time, 
                            start_date = datetime.utcnow().date(), 
                            end_date = food.expiration_date,
                            session = session)
                session.commit()
            except Exception as e:
                print(e)
                text = "鬧鐘提醒時間修改失敗"
                session.rollback()
            else:
                text = f"鬧鐘提醒時間已改為 {new_time}"
            finally:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=text))
                session.close()

    elif action == "addFood": # OK
        food_name = pb_data.split("=")[1]
        exp_date = event.postback.params['date']
        with Session() as session:
            try:
                crud.add_food(
                    name = food_name, 
                    user_id = event.source.user_id,
                    exp_date = exp_date,
                    session = session)
                session.commit()
            except Exception as e:
                print(e)
                text = "新增食物失敗"
                session.rollback()
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
            finally:
                session.close()

    elif action == "finished": # OK
        food_id = int(pb_data.split("=")[1])
        with Session() as session:
            try:
                crud.update_food_status(food_id = food_id, session = session)
                session.commit()
            except Exception as e:
                print(e)
                text = "吃完食物失敗"
                session.rollback()
            else:
                text = "已吃完！"
            finally:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=text))
                session.close()

def send_alarm_message(user_id: str, food_name: str, food_exp_date):
    try:
        text = f"提醒！{food_name} 將在 {dt_converter.date_to_str(food_exp_date)} 過期"
        line_bot_api.push_message(
            user_id, 
            TextSendMessage(text=text))
    except LineBotApiError as e:
        print("失敗~~~~")