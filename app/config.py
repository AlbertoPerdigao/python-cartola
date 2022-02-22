import os
from app.database import HOST, DATABASE, PORT, USER, PASSWORD


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PROPAGATE_EXCEPTIONS = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "postgresql://{}:{}@{}:{}/{}".format(USER, PASSWORD, HOST, PORT, DATABASE)
