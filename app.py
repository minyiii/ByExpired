from __future__ import unicode_literals
from datetime import date, datetime, timedelta
import os
import sys
import json
import ast
from argparse import ArgumentParser
from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (MessageEvent, PostbackEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, 
MessageAction, DatetimePickerAction, FlexSendMessage, TemplateSendMessage, ConfirmTemplate, PostbackAction)
from dotenv import load_dotenv
from utils import get_food_jsons, get_edit_jsons
load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI')
db = SQLAlchemy(app)

from models import User, Alarm, Food

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
    if option_text == "查看品項":
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(
                alt_text = '給你看',
                contents = get_food_jsons()
            )
        )
    elif option_text.startswith("取消"):
        pass
    elif option_text[0]=="+":
        food_name = option_text[1:]
        confirm_msg = TemplateSendMessage(
            alt_text = "新增品項", 
            template = ConfirmTemplate(
                text = f"你要新增 {food_name} 對嗎",
                actions = [
                    DatetimePickerAction(
                        label= "選擇有效期限", 
                        data = "action=addFood&name={}".format(food_name), 
                        min = datetime.utcnow().strftime('%Y-%m-%d'),
                        mode ="date"),
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

    if action == "edit":
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(
                alt_text = '請進行編輯',
                contents = get_edit_jsons("Eggs!")
            )
        )
    elif action == "setExpDate":
        new_exp_date = event.postback.params['date']
        food_id = int(pb_data.split("=")[1])
        # 進DB改
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"有效期限已改為 {new_exp_date}"))
    elif action == "setAlarmStart":
        new_alarm_start = event.postback.params['date']
        alarm_id = int(pb_data.split("=")[1])
        # 進DB改（要確定是否在有效期限前）
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"開始提醒日已改為 {new_alarm_start}"))
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
    elif action == "setAlarmTiming":
        new_alarm = event.postback.params['time']
        alarm_id = int(pb_data.split("=")[1])
        # 進DB改
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"鬧鐘已改為 {new_alarm}"))
    elif action == "addFood":
        food_name = pb_data.split("=")[1]
        exp_date = datetime.strptime(event.postback.params['date'], '%Y-%m-%d').date()
        
        # 寫到DB
        text = f"已新增 {exp_date.strftime('%Y/%m/%d')} 過期的{food_name}"
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

    elif action == "finished":
        food_id = int(pb_data.split("=")[1])
        # 進DB改
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"已吃完 {food_id}！"))
    text_message = TextSendMessage(text="看不懂你在說什麼")
    line_bot_api.reply_message(event.reply_token, text_message)

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
