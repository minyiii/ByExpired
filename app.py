from __future__ import unicode_literals
import os
import sys
from argparse import ArgumentParser
from flask import Flask, request, abort
from flask.logging import create_logger

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import configparser
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
LOG = create_logger(app)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')

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
    if option_text == "新增品項":
        pass
    elif option_text == "查看品項":
        pass
    elif option_text == "清理品項":
        pass
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"Hi, {profile.display_name}, 你要{option_text}喔"))


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
