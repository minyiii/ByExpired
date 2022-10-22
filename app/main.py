'''
Flask route
'''
from flask import request, abort
from linebot.exceptions import InvalidSignatureError
from app import app, db
from app.api import handler

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