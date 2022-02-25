from decimal import Decimal
from flask import request
from flask_restful import Resource
from models.month import MonthModel
from models.score import ScoreModel
from models.winner import WinnerModel
from resources.cartola_api import CartolaApi
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
    OBJECT_DELETED_SUCCESSFULLY    
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


class WinnerPrizesCalculation(Resource):
    @classmethod
    def get(cls):
        from models.month import MonthModel        

        # Calculates the winners and prizes of the current month/year for each type of award

        # Finds the current month by the round_number and current year        
                
        cartola_status = CartolaApi.get_cartola_status()
        #current_year = cartola_status["temporada"] #datetime.datetime.now().year
        #current_round_number = cartola_status["rodada_atual"]
        ### remove this code snippet when Cartola API is working, replacing it with the 2 lines above
        current_round_number = 3
        current_year = 2022
        ###
        
        print(current_year)
        try:
            current_month = MonthModel.find_by_round_number_year(current_round_number, current_year)            
        except:
            return {"message": ERROR_GETTING_OBJECT.format("Month")}, 500
        
        if not current_month:
            return {"message": ERROR_GETTING_OBJECT.format("Month")}, 500

        print("current month: {}".format(current_month))
        
        cls.__calculates_winners_prize_mes(current_month)

        return {"message": "WinnerPrizesCalculation finished with success"}
    
    def __calculates_winners_prize_mes(current_month: MonthModel):
        from models.payment import PaymentModel
        from models.prize import PrizeModel

        print("Prize - Mês - Current Month: {}".format(current_month.id))

        # The winners will be those who have the highest sum of points from the rounds of the month

        # Gets the rounds of the current month
        #rounds = current_month.rounds

        # Gets the payments amout and the prize "Mês" of the current month

        try:
            payments = PaymentModel.find_all_by_months_id(current_month.id)
        except:
            return {"message": ERROR_GETTING_OBJECTS.format("Payments")}, 500

        total_payments_amount = 0
        for payment in payments:
            total_payments_amount += payment.amount
        print("total_payments_amount: {}".format(total_payments_amount))
                
        try:
            prize = PrizeModel.find_by_name_months_id("Mês", current_month.id)            
        except:
            return {"message": ERROR_GETTING_OBJECT.format("Prize")}, 500

        print(prize)                
        total_prize_value = (prize.total_prize_percentage * total_payments_amount) / 100            
        total_prize_value = total_prize_value.quantize(Decimal('.01'))
        print("total_prize_value: {}".format(total_prize_value))               
         
        # Get the scores in the month

        try:
            sorted_scores = ScoreModel.sum_scores_by_months_id(current_month.id)
        except:
            return {"message": ERROR_GETTING_OBJECTS.format("Score")}, 500
        
        if not sorted_scores:
            return {"message": ERROR_GETTING_OBJECTS.format("Score")}, 500
        
        print(sorted_scores)        
        
        #sorted_scores = sorted(scores, key=lambda s: s.value, reverse=True)
        #print("sorted_scores: {}".format(sorted_scores))

        # Updates their prize value according to the amount of people who paid the monthly fee, their places and prize type
        
        place = 1
        for score in sorted_scores:
            teams_id = score[1]

            try:
                winner = WinnerModel.find_by_teams_id_prizes_id(teams_id, prize.id)
            except:
                return {"message": ERROR_GETTING_OBJECT.format(Winner.__name__)}, 500
            
            if not winner:            
                winner = WinnerModel()
                winner.teams_id = score[1]
                winner.prizes_id = prize.id
            
            winner.place = place

            if place == 1:                                
                winner.prize_value = (total_prize_value * prize.first_place_percentage) / 100
                print("1st:{}".format(winner))
            elif place == 2:                
                winner.prize_value = (total_prize_value * prize.second_place_percentage) / 100
                print("2nd:{}".format(winner))
            elif place == 3:
                winner.prize_value = (total_prize_value * prize.tird_place_percentage) / 100
                print("3rd:{}".format(winner))
            elif place == 4:
                winner.prize_value = (total_prize_value * prize.fourth_place_percentage) / 100
                print("4th:{}".format(winner))

            try:
                winner.save_to_db()
            except:
                return {"message": ERROR_INSERTING_OBJECT.format(Winner.__name__)}, 500
            
            if place == 4:
                break

            place += 1
            