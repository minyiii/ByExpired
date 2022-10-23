'''
ref: https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/quickstart/#configure-the-extension
ref: https://www.youtube.com/watch?v=WhwU1-DLeVw
'''

import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from flask_migrate import Migrate
from flask_apscheduler import APScheduler

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI')
app.config['SCHEDULER_API_ENABLED'] = True
app.config['SCHEDULER_TIMEZONE'] = 'Asia/Taipei'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
Session = db.session

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

from app import main # ref: https://stackoverflow.com/questions/11994325/how-to-divide-flask-app-into-multiple-py-files
from app import jobs # ref: https://viniciuschiele.github.io/flask-apscheduler/rst/tips.html