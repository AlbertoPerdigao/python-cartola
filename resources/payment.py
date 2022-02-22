from flask_restful import Resource
from flask import request
from models.payment import PaymentModel
from schemas.payment import PaymentSchema
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

payment_schema = PaymentSchema()
payment_list_schema = PaymentSchema(many=True)


class Payment(Resource):
    @classmethod
    def get(cls, id: int):
        try:
            payment = PaymentModel.find_by_id(id)
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if payment:
            return payment_schema.dump(payment)

        return {"message": OBJECT_NOT_FOUND.format(cls.__name__)}, 404

    @classmethod
    def post(cls, id: int):
        payment_json = request.get_json()
        payment = payment_schema.load(payment_json)  # Validates the fields

        try:
            payment_exists = PaymentModel.find_by_team_id_month_id(
                payment_json["teams_id"], payment_json["months_id"]
            )
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if payment_exists:
            return {"message": OBJECT_ALREADY_EXISTS.format(cls.__name__)}, 400

        try:
            payment.save_to_db()
        except:
            return {"message": ERROR_INSERTING_OBJECT.format(cls.__name__)}, 500

        return {"message": OBJECT_CREATED_SUCCESSFULLY.format(cls.__name__)}, 201

    @classmethod
    def put(cls, id: int):
        payment_json = request.get_json()
        modified_payment = payment_schema.load(
            payment_json,
            partial=(
                "teams_id",
                "months_id",
            ),
        )  # Validates the fields / partial -> not required

        try:
            payment = PaymentModel.find_by_id(id)
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if not payment:
            return {"message": OBJECT_NOT_FOUND.format(cls.__name__)}, 404

        payment.amount = modified_payment.amount

        try:
            payment.save_to_db()
        except:
            return {"message": ERROR_UPDATING_OBJECT.format(cls.__name__)}, 500

        return payment_schema.dump(payment), 200

    @classmethod
    def delete(cls, id: int):
        try:
            payment = PaymentModel.find_by_id(id)
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if payment:
            try:
                payment.delete_from_db()
                return {
                    "message": OBJECT_DELETED_SUCCESSFULLY.format(cls.__name__)
                }, 200
            except:
                return {"message": ERROR_DELETING_OBJECT.format(cls.__name__)}, 500

        return {"message": OBJECT_NOT_FOUND.format(cls.__name__)}, 404


class PaymentList(Resource):
    @classmethod
    def get(cls, year: int):
        try:
            payments = PaymentModel.find_all_by_year(year)
        except:
            return {"message": ERROR_GETTING_OBJECTS.format(cls.__name__)}, 500

        return {"payments": payment_list_schema.dump(payments)}, 200
