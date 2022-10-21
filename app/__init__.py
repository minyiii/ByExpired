'''
ref: https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/quickstart/#configure-the-extension
ref: https://www.youtube.com/watch?v=WhwU1-DLeVw
'''

import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from flask_migrate import Migrate

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI')
db = SQLAlchemy(app)
# migrate = Migrate(app, db)

from app import api # ref: https://stackoverflow.com/questions/11994325/how-to-divide-flask-app-into-multiple-py-files