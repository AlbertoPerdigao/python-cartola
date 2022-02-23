import datetime, requests
from decimal import Decimal
from flask_restful import Resource
from flask import request
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
    ERROR_GETTING_STATUS_CARTOLA
)

winner_schema = WinnerSchema()
winner_list_schema = WinnerSchema(many=True)
CARTOLA_STATUS_URI = "https://api.cartolafc.globo.com/mercado/status"

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


class WinnerPrizesCalculation(Resource):
    @classmethod
    def get(cls):
        from models.payment import PaymentModel
        from models.month import MonthModel

        # Calculates the winners prizes of the current month/year

        # Finds the current month by the round_number and current year
        #   The current round is obtained by the Cartola FC api (https://api.cartolafc.globo.com/mercado/status)
        # Get the winners of the current month
        # Updates their prize value according to the amount of people who paid the monthly fee, their places and prize type

        current_year = datetime.datetime.now().year        
        
        try:
            status_cartola = requests.get(CARTOLA_STATUS_URI).json()
        except requests.ConnectionError:
            return {"message": ERROR_GETTING_STATUS_CARTOLA}, 500
        
        #current_round_number = status_cartola["rodada_atual"]        
        current_round_number = 3

        current_month = MonthModel.find_by_round_number_year(current_round_number, current_year)
        print("current month: {}".format(current_month))

        try:
            payments = PaymentModel.find_all_by_months_id(current_month.id)
        except:
            return {"message": ERROR_GETTING_OBJECTS.format(PaymentModel.__name__)}, 500

        total_payments_amount = 0
        for payment in payments:
            total_payments_amount += payment.amount        
        print("total_payments_amount: {}".format(total_payments_amount))


        # TO DO
        # Get the winners through the Cartola's FC api

        #get_month_winners(current_month.id)

        try:
            winners = WinnerModel.find_all_by_months_id(current_month.id)
        except:
            return {"message": ERROR_GETTING_OBJECTS.format(WinnerModel.__name__)}, 500

        if not winners:
            winner1 = WinnerModel()
            winner1.place = 1
            winner1.teams_id = 20
            winner1.prizes_id = 1

        for winner in winners:
            print(winner)
            total_prize_percentage = winner.prize.total_prize_percentage
            #total_prize_value = (Decimal(total_prize_percentage) * Decimal(total_payments_amount)) / Decimal(100)
            total_prize_value = (total_prize_percentage * total_payments_amount) / 100            
            total_prize_value = total_prize_value.quantize(Decimal('.01'))
            print(total_prize_value)

            if winner.place == 1:

                winner.prize_value = 1

            elif winner.place == 2:
                winner.prize_value = 2
            elif winner.place == 3:
                winner.prize_value = 3
            elif winner.place == 4:
                winner.prize_value = 4
