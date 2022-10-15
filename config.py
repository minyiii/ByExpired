import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URI')
