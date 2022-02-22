from flask_restful import Resource
from flask import request
from models.round import RoundModel
from schemas.round import RoundSchema
from app.messages import (
    OBJECT_NOT_FOUND,
    OBJECT_ALREADY_EXISTS,
    ERROR_GETTING_OBJECT,
    ERROR_GETTING_OBJECTS,
    ERROR_INSERTING_OBJECT,
    ERROR_UPDATING_OBJECT,
    ERROR_DELETING_OBJECT,
    OBJECT_CREATED_SUCCESSFULLY,
    OBJECT_DELETED_SUCCESSFULLY,
)

round_schema = RoundSchema()
round_list_schema = RoundSchema(many=True)


class Round(Resource):
    @classmethod
    def get(cls, id: int):
        try:
            round = RoundModel.find_by_id(id)
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if round:
            return round_schema.dump(round)

        return {"message": OBJECT_NOT_FOUND.format(cls.__name__)}, 404

    @classmethod
    def post(cls, id: int):
        round_json = request.get_json()
        round = round_schema.load(round_json)  # Validates the fields

        try:
            rounds = RoundModel.find_rounds_by_year(
                round.months_id
            )  # find the rounds of the year to avoid repetition
        except:
            return {"message": ERROR_GETTING_OBJECTS.format(cls.__name__)}, 500

        if round.round_number in rounds:
            return {"message": OBJECT_ALREADY_EXISTS.format(cls.__name__)}, 400

        try:
            round.save_to_db()
        except:
            return {"message": ERROR_INSERTING_OBJECT.format(cls.__name__)}, 500

        return {"message": OBJECT_CREATED_SUCCESSFULLY.format(cls.__name__)}, 201

    @classmethod
    def put(cls, id: int):
        round_json = request.get_json()
        modified_round = round_schema.load(
            round_json, partial=("round_number",)
        )  # Validates the fields

        try:
            round = RoundModel.find_by_id(id)  # find the round to update
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if not round:
            return {"message": OBJECT_NOT_FOUND.format(cls.__name__)}, 404

        round.months_id = modified_round.months_id
        round.awarded = modified_round.awarded

        try:
            round.save_to_db()
        except:
            return {"message": ERROR_UPDATING_OBJECT.format(cls.__name__)}, 500

        return round_schema.dump(round), 200

    @classmethod
    def delete(cls, id: int):
        try:
            round = RoundModel.find_by_id(id)
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if round:
            try:
                round.delete_from_db()
                return {
                    "message": OBJECT_DELETED_SUCCESSFULLY.format(cls.__name__)
                }, 200
            except:
                return {"message": ERROR_DELETING_OBJECT.format(cls.__name__)}, 500

        return {"message": OBJECT_NOT_FOUND.format(cls.__name__)}, 404


class RoundList(Resource):
    @classmethod
    def get(cls, year: int):
        try:
            rounds = RoundModel.find_all_by_year(year)
        except:
            return {"message": ERROR_GETTING_OBJECTS.format(cls.__name__)}, 500

        return {"rounds": round_list_schema.dump(rounds)}, 200
