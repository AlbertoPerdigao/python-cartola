import os
from app.database import HOST, DATABASE, PORT, USER, PASSWORD


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PROPAGATE_EXCEPTIONS = True
    uri = os.getenv('DATABASE_URL') #or "postgresql://{}:{}@{}:{}/{}".format(USER, PASSWORD, HOST, PORT, DATABASE)
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    print("POSTGRES: {}".format(uri))
    SQLALCHEMY_DATABASE_URI = uri
