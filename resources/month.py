from flask_restful import Resource
from flask import request
from models.month import MonthModel
from schemas.month import MonthSchema
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

month_schema = MonthSchema()
month_list_schema = MonthSchema(many=True)


class Month(Resource):
    @classmethod
    def get(cls, id: int):
        try:
            month = MonthModel.find_by_id(id)
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if month:
            return month_schema.dump(month)

        return {"message": OBJECT_NOT_FOUND.format(cls.__name__)}, 404

    @classmethod
    def post(cls, id: int):
        month_json = request.get_json()
        month = month_schema.load(month_json)  # Validates the fields

        try:
            month_exists = MonthModel.find_by_name_year(month.name, month.year)
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if month_exists:
            return {"message": OBJECT_ALREADY_EXISTS.format(cls.__name__)}, 400

        try:
            month.save_to_db()
        except:
            return {"message": ERROR_INSERTING_OBJECT.format(cls.__name__)}, 500

        return {"message": OBJECT_CREATED_SUCCESSFULLY.format(cls.__name__)}, 201

    @classmethod
    def put(cls, id: int):
        month_json = request.get_json()
        modified_month = month_schema.load(month_json)  # Validates the fields

        try:
            month_already_exists = MonthModel.find_by_name_year(
                modified_month.name, modified_month.year
            )
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if month_already_exists:
            return {"message": OBJECT_ALREADY_EXISTS.format(cls.__name__)}, 400

        try:
            month = MonthModel.find_by_id(id)
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if not month:
            return {"message": OBJECT_NOT_FOUND.format(cls.__name__)}, 404

        month.name = modified_month.name
        month.year = modified_month.year
        month.tax = modified_month.tax

        try:
            month.save_to_db()
        except:
            return {"message": ERROR_UPDATING_OBJECT.format(cls.__name__)}, 500

        return month_schema.dump(month), 200

    @classmethod
    def delete(cls, id: int):
        try:
            month = MonthModel.find_by_id(id)
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if month:
            try:
                month.delete_from_db()
                return {
                    "message": OBJECT_DELETED_SUCCESSFULLY.format(cls.__name__)
                }, 200
            except:
                return {"message": ERROR_DELETING_OBJECT.format(cls.__name__)}, 500

        return {"message": OBJECT_NOT_FOUND.format(cls.__name__)}, 404


class MonthList(Resource):
    @classmethod
    def get(cls, year: int):
        try:
            months = MonthModel.find_all_by_year(year)
        except:
            return {"message": ERROR_GETTING_OBJECTS.format(cls.__name__)}, 500

        return {"months": month_list_schema.dump(months)}, 200
