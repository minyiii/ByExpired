from __future__ import unicode_literals
import os
import sys
from flask import Flask, request, abort
from flask.logging import create_logger

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import configparser


app = Flask(__name__)
LOG = create_logger(app)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')

channel_access_token = config.get('line-bot', 'channel_access_token')
channel_secret = config.get('line-bot', 'channel_secret')

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
    text = event.message.text
    if text == "新增品項":
        pass
    elif text == "查看品項":
        pass
    elif text == "清理品項":
        pass
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    app.run()
