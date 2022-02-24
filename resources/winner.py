from flask_restful import Resource
from flask import request
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
        from models.payment import PaymentModel
        from models.month import MonthModel
        from models.prize import PrizeModel

        # Calculates the winners and prizes of the current month/year

        # Finds the current month by the round_number and current year        
                
        cartola_status = CartolaApi.get_cartola_status()
        #current_round_number = cartola_status["rodada_atual"]
        current_round_number = 3
        current_year = cartola_status["temporada"] #datetime.datetime.now().year

        current_month = MonthModel.find_by_round_number_year(current_round_number, current_year)
        print("current month: {}".format(current_month))
        month_rounds = current_month.rounds

        # Gets the payments amout and the prizes of the current month

        try:
            payments = PaymentModel.find_all_by_months_id(current_month.id)
        except:
            return {"message": ERROR_GETTING_OBJECTS.format(PaymentModel.__name__)}, 500

        total_payments_amount = 0
        for payment in payments:
            total_payments_amount += payment.amount        
        print("total_payments_amount: {}".format(total_payments_amount))

        
        prizes = PrizeModel.find_by_months_id(current_month.id)
        print(prizes)


        # TO DO
        # Get the scores through the Cartola FC api
        # Get the winners through the scores

        #teams_scores = ScoreTeam.get_teams_scores_by_months_id(current_month.id, current_round_number) 
       
        #for s in teams_scores
        #    ScoreModel.update_scores(s.nome, s.rodada, s.pontuacao)

        try:
            scores = ScoreModel.find_all_by_months_id(current_month.id)
        except:
            return {"message": ERROR_GETTING_OBJECTS.format(WinnerModel.__name__)}, 500
        
        sorted_scores = sorted(scores, key=lambda s: s.value, reverse=True)
        print(sorted_scores)

               
        # Updates their prize value according to the amount of people who paid the monthly fee, their places and prize type

        count = 1
        for score in sorted_scores:
            winner = WinnerModel()
            winner.teams_id = score.teams_id
            #winner.prizes_id = score.

            if count == 1:
                print("1st:{}".format(score.team.name))
                winner.place = 1
                
                
            elif count == 2:
                print("2nd:{}".format(score.team.name))
            elif count == 3:
                print("3rd:{}".format(score.team.name))
            elif count == 4:
                print("4th:{}".format(score.team.name))
                break            
            count += 1                        
            
        """
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
        """