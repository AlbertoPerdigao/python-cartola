import requests
from flask_restful import Resource
from flask import request
from models.score import ScoreModel
from schemas.score import ScoreSchema
from app.messages import (
    OBJECT_NOT_FOUND,
    OBJECT_ALREADY_EXISTS,
    ERROR_GETTING_OBJECT,
    ERROR_GETTING_OBJECTS,
    ERROR_INSERTING_OBJECT,
    ERROR_UPDATING_OBJECT,
    ERROR_DELETING_OBJECT,
    OBJECT_CREATED_SUCCESSFULLY,
    OBJECT_DELETED_SUCCESSFULLY    
)

score_schema = ScoreSchema()
score_list_schema = ScoreSchema(many=True)
#CARTOLA_STATUS_URI = "https://api.cartolafc.globo.com/mercado/status"

class Score(Resource):
    @classmethod
    def get(cls, id: int):
        try:
            score = ScoreModel.find_by_id(id)
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if score:
            return score_schema.dump(score)

        return {"message": OBJECT_NOT_FOUND.format(cls.__name__)}, 404

    @classmethod
    def post(cls, id: int):
        score_json = request.get_json()
        score = score_schema.load(score_json)  # Validates the fields
        
        try:
            score_exists = ScoreModel.find_by_teams_id_rounds_id(
                score.teams_id, score.rounds_id
            )
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if score_exists:
            return {"message": OBJECT_ALREADY_EXISTS.format(cls.__name__)}, 400

        try:
            score.save_to_db()
        except:
            return {"message": ERROR_INSERTING_OBJECT.format(cls.__name__)}, 500
        
        return {"message": OBJECT_CREATED_SUCCESSFULLY.format(cls.__name__)}, 201

    @classmethod
    def put(cls, id: int):
        score_json = request.get_json()
        modified_score = score_schema.load(
            score_json, partial=("teams_id", "rounds_id")
        )  # Validates the fields

        try:
            score = ScoreModel.find_by_id(id)  # find the score to update
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if not score:
            return {"message": OBJECT_NOT_FOUND.format(cls.__name__)}, 404

        score.points = modified_score.points

        try:
            score.save_to_db()
        except:
            return {"message": ERROR_UPDATING_OBJECT.format(cls.__name__)}, 500

        return score_schema.dump(score), 200

    @classmethod
    def delete(cls, id: int):
        try:
            score = ScoreModel.find_by_id(id)
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if score:
            try:
                score.delete_from_db()
                return {
                    "message": OBJECT_DELETED_SUCCESSFULLY.format(cls.__name__)
                }, 200
            except:
                return {"message": ERROR_DELETING_OBJECT.format(cls.__name__)}, 500

        return {"message": OBJECT_NOT_FOUND.format(cls.__name__)}, 404


class ScoreList(Resource):
    @classmethod
    def get(cls, year: int):
        try:
            scores = ScoreModel.find_all_by_year(year)
        except:
            return {"message": ERROR_GETTING_OBJECTS.format(cls.__name__)}, 500

        return {"scores": score_list_schema.dump(scores)}, 200