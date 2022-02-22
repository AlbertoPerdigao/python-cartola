from marshmallow import ValidationError
from flask import jsonify
from app import app


@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify(err.messages), 400
