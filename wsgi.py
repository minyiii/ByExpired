# ref: https://github.com/PrettyPrinted/youtube_video_code/blob/daf426f0f1fb64cee66169f91111a6e7dbbc85cf/2019/07/25/Deploy%20a%20Flask%20App%20to%20Heroku%20With%20a%20Postgres%20Database%20%5B2019%5D/flask_qa/wsgi.py
import os
from app import app
from argparse import ArgumentParser

if __name__ == '__main__':
    # Flask app
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )

    http_port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=http_port)