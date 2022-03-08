from flask_restful import Resource
from flask import request
from models.prize import PrizeModel
from schemas.prize import PrizeSchema
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

prize_schema = PrizeSchema()
prize_list_schema = PrizeSchema(many=True)


class Prize(Resource):
    @classmethod
    def get(cls, id: int):
        try:
            prize = PrizeModel.find_by_id(id)
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if prize:
            return prize_schema.dump(prize)
        return {"message": OBJECT_NOT_FOUND.format(cls.__name__)}, 404

    @classmethod
    def post(cls, id: int):
        prize_json = request.get_json()
        prize = prize_schema.load(prize_json)  # Validates the fields

        try:
            prize_exists = PrizeModel.find_by_name_months_id(
                prize_json["name"], prize_json["months_id"]
            )
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if prize_exists:
            return {"message": OBJECT_ALREADY_EXISTS.format(cls.__name__)}, 400

        try:
            prize.save_to_db()
        except:
            return {"message": ERROR_INSERTING_OBJECT.format(cls.__name__)}, 500

        return {"message": OBJECT_CREATED_SUCCESSFULLY.format(cls.__name__)}, 201

    @classmethod
    def put(cls, id: int):
        prize_json = request.get_json()
        modified_prize = prize_schema.load(
            prize_json,
            partial=(
                "months_id",
                "rounds_id",
            ),
        )  # Validates the fields

        try:
            prize = PrizeModel.find_by_id(id)  # find the prize to update
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if not prize:
            return {"message": OBJECT_NOT_FOUND.format(cls.__name__)}, 404

        prize.name = modified_prize.name
        prize.total_prize_percentage = modified_prize.total_prize_percentage
        prize.first_place_percentage = modified_prize.first_place_percentage
        prize.second_place_percentage = modified_prize.second_place_percentage
        prize.tird_place_percentage = modified_prize.tird_place_percentage
        prize.fourth_place_percentage = modified_prize.fourth_place_percentage
        if modified_prize.rounds_id:
            prize.rounds_id = modified_prize.rounds_id

        try:
            prize.save_to_db()
        except:
            return {"message": ERROR_UPDATING_OBJECT.format(cls.__name__)}, 500

        return prize_schema.dump(prize), 200

    @classmethod
    def delete(cls, id: int):
        try:
            prize = PrizeModel.find_by_id(id)
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if prize:
            try:
                prize.delete_from_db()
                return {
                    "message": OBJECT_DELETED_SUCCESSFULLY.format(cls.__name__)
                }, 200
            except:
                return {"message": ERROR_DELETING_OBJECT.format(cls.__name__)}, 500

        return {"message": OBJECT_NOT_FOUND.format(cls.__name__)}, 404


class PrizeList(Resource):
    @classmethod
    def get(cls, year: int):
        try:
            prizes = PrizeModel.find_all_by_year(year)
        except:
            return {"message": ERROR_GETTING_OBJECTS.format(cls.__name__)}, 500

        return {"prizes": prize_list_schema.dump(prizes)}, 200
