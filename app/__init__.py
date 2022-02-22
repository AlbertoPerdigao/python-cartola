from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)
api = Api(app)

# app.config['SQLALCHEMY_DATABASE_URI'] = uri #os.getenv('DATABASE_URL')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['PROPAGATE_EXCEPTIONS'] = True
# app.secret_key = 'secret_key'

from app import routes, error_handler
from models import team, month, payment, prize, round, winner, time_mixin
from schemas import team, month, payment, prize, round, winner
