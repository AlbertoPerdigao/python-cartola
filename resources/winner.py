from flask import request
from flask_restful import Resource
from models.winner import WinnerModel
from schemas.winner import WinnerSchema
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

winner_schema = WinnerSchema()
winner_list_schema = WinnerSchema(many=True)


class Winner(Resource):
    @classmethod
    def get(cls, id: int):
        try:
            winner = WinnerModel.find_by_id(id)
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if winner:
            return winner_schema.dump(winner)

        return {"message": OBJECT_NOT_FOUND.format(cls.__name__)}, 404

    @classmethod
    def post(cls, id: int):
        winner_json = request.get_json()
        winner = winner_schema.load(winner_json)  # Validates the fields

        try:
            winner_exists = WinnerModel.find_by_teams_id_prizes_id(
                winner.teams_id, winner.prizes_id
            )
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if winner_exists:
            return {"message": OBJECT_ALREADY_EXISTS.format(cls.__name__)}, 400

        try:
            winner.save_to_db()
        except:
            return {"message": ERROR_INSERTING_OBJECT.format(cls.__name__)}, 500

        return {"message": OBJECT_CREATED_SUCCESSFULLY.format(cls.__name__)}, 201

    @classmethod
    def put(cls, id: int):
        winner_json = request.get_json()
        modified_winner = winner_schema.load(
            winner_json, partial=("teams_id", "prizes_id")
        )  # Validates the fields

        try:
            winner = WinnerModel.find_by_id(id)  # find the winner to update
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if not winner:
            return {"message": OBJECT_NOT_FOUND.format(cls.__name__)}, 404

        winner.place = modified_winner.place
        winner.prize_value = modified_winner.prize_value

        try:
            winner.save_to_db()
        except:
            return {"message": ERROR_UPDATING_OBJECT.format(cls.__name__)}, 500

        return winner_schema.dump(winner), 200

    @classmethod
    def delete(cls, id: int):
        try:
            winner = WinnerModel.find_by_id(id)
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if winner:
            try:
                winner.delete_from_db()
                return {
                    "message": OBJECT_DELETED_SUCCESSFULLY.format(cls.__name__)
                }, 200
            except:
                return {"message": ERROR_DELETING_OBJECT.format(cls.__name__)}, 500

        return {"message": OBJECT_NOT_FOUND.format(cls.__name__)}, 404


class WinnerList(Resource):
    @classmethod
    def get(cls, year: int):
        try:
            winners = WinnerModel.find_all_by_year(year)
        except:
            return {"message": ERROR_GETTING_OBJECTS.format(cls.__name__)}, 500

        return {"winners": winner_list_schema.dump(winners)}, 200
