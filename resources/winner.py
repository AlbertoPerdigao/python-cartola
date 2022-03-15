from decimal import Decimal, ROUND_UP
from typing import List
from werkzeug.security import safe_str_cmp
from flask import request
from flask_restful import Resource
from models.month import MonthModel
from models.prize import PrizeModel
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
    OBJECT_DELETED_SUCCESSFULLY,
)

winner_schema = WinnerSchema()
winner_list_schema = WinnerSchema(many=True)
RODADA_PREMIADA_PRIZE = "Rodada Premiada"
MES_PRIZE = "Mês"
TURNO_PRIZE = "Turno"
COPA_DA_LIGA_PRIZE = "Copa da Liga"
PATRIMONIO_PRIZE = "Patrimônio"


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
        from resources.score import ScoreCartolaUpdate
        from models.payment import PaymentModel

        # Calculates the winners and prizes of the current month/year for each type of award

        # Finds the current month by the round_number and current year

        cartola_status = CartolaApi.get_cartola_status()
        current_year = cartola_status["temporada"]  # datetime.datetime.now().year
        current_round_number = cartola_status["rodada_atual"]
        print(
            "cartola_status -> year: {}, round: {}".format(
                current_year, current_round_number
            )
        )
        ### remove this code snippet when Cartola API is working
        current_round_number = 3
        current_year = 2022
        print("year: {}, round: {}".format(current_year, current_round_number))
        ###

        # Updates the teams scores trough the current round an year
        ScoreCartolaUpdate.update_teams_scores(current_round_number, current_year)

        try:
            current_month = MonthModel.find_by_round_number_year(
                current_round_number, current_year
            )
        except:
            return {"message": ERROR_GETTING_OBJECT.format("Month")}, 500

        if not current_month:
            return {"message": ERROR_GETTING_OBJECT.format("Month")}, 500

        print("current month: {}".format(current_month))

        # Gets the current month's payment amount
        try:
            payments = PaymentModel.find_all_by_months_id(current_month.id)
        except:
            return {"message": ERROR_GETTING_OBJECTS.format("Payments")}, 500

        total_payments_amount = 0
        for payment in payments:
            total_payments_amount += payment.amount

        for prize in current_month.prizes:
            if safe_str_cmp(prize.name, MES_PRIZE):
                cls.__calculates_mes_prize_winners(
                    current_month, total_payments_amount, prize
                )
            elif (
                safe_str_cmp(prize.name, RODADA_PREMIADA_PRIZE)
                and prize.round.round_number == current_round_number
                and prize.round.awarded
            ):
                cls.__calculates_rodada_premiada_prize_winners(
                    current_month, total_payments_amount, prize
                )
            elif safe_str_cmp(prize.name, COPA_DA_LIGA_PRIZE):
                print("Copa da Liga")
            elif safe_str_cmp(prize.name, PATRIMONIO_PRIZE):
                print("Patrimônio")

        # Gets the amount of payments for the current shift months
        try:
            months_ids = MonthModel.find_shift_months_ids_by_round_number_year(
                current_round_number, current_year
            )
        except:
            return {"message": ERROR_GETTING_OBJECTS.format("MonthModel")}, 500

        total_payments_amount = 0
        months_ids_list = list()
        for month in months_ids:
            try:
                payments = PaymentModel.find_all_by_months_id(month.id)
                months_ids_list.append(month.id)
            except:
                return {"message": ERROR_GETTING_OBJECTS.format("Payments")}, 500

            for payment in payments:
                total_payments_amount += payment.amount

        cls.__calculates_turno_prize_winners(
            months_ids_list, current_round_number, total_payments_amount
        )

        return {"message": "{} finished with success".format(cls.__name__)}

    @classmethod
    def __calculates_turno_prize_winners(
        cls, months_ids_list, current_round_number, total_payments_amount
    ) -> None:
        print("Prize: {} - Round: {}".format(TURNO_PRIZE, current_round_number))

        # The winners will be those who have the highest number of points in the current shift
        # The shifts are divided in 2: shift 1 - round 1 to 19 and shift 2 - round 20 to 38

        turno_prizes = PrizeModel.find_by_name(TURNO_PRIZE)
        for turno_prize in turno_prizes:
            if (
                turno_prize.round.round_number == 19 and current_round_number <= 19
            ) or (turno_prize.round.round_number == 38 and current_round_number > 19):
                prize = turno_prize

        if not prize:
            return {"message": ERROR_GETTING_OBJECT.format("Prize")}, 500

        total_prize_value = (
            (prize.total_prize_percentage * total_payments_amount) / 100
        ).quantize(Decimal(".01"))

        # Gets the scores of the shift
        try:
            sorted_scores = ScoreModel.sum_teams_scores_by_list_months_id(
                months_ids_list
            )
        except:
            return {"message": ERROR_GETTING_OBJECTS.format("Score")}, 500

        if not sorted_scores:
            return {"message": ERROR_GETTING_OBJECTS.format("Score")}, 500

        cls.__updates_winners(prize, sorted_scores, total_prize_value)

    @classmethod
    def __calculates_rodada_premiada_prize_winners(
        cls,
        current_month: MonthModel,
        total_payments_amount: Decimal,
        prize: PrizeModel,
    ) -> None:

        print(
            "Prize: {} - Current Month: {} - Round: {}".format(
                prize.name, current_month.id, prize.round.round_number
            )
        )

        # The winners will be those who have the highest number of points in the current awarded round of the month

        # Gets the number of awarded rounds in the month
        awarded_rounds = 0
        for round in current_month.rounds:
            if round.awarded:
                awarded_rounds += 1

        month_prize_value = (
            (prize.total_prize_percentage * total_payments_amount) / 100
        ).quantize(Decimal(".01"))
        round_prize_value = (month_prize_value / awarded_rounds).quantize(
            Decimal(".01")
        )

        # Get the scores of the round
        try:
            scores = ScoreModel.find_by_rounds_id(prize.round.round_number)
        except:
            return {"message": ERROR_GETTING_OBJECTS.format("Score")}, 500

        if not scores:
            return {"message": ERROR_GETTING_OBJECTS.format("Score")}, 500

        sorted_scores = sorted(scores, key=lambda s: s.value, reverse=True)

        cls.__updates_winners(prize, sorted_scores, round_prize_value)

    @classmethod
    def __calculates_mes_prize_winners(
        cls,
        current_month: MonthModel,
        total_payments_amount: Decimal,
        prize: PrizeModel,
    ) -> None:

        print("Prize: {} - Current Month: {}".format(prize.name, current_month.id))

        # The winners will be those who have the highest sum of points from the rounds of the month

        total_prize_value = (
            (prize.total_prize_percentage * total_payments_amount) / 100
        ).quantize(Decimal(".01"))

        # Gets the scores of the month
        try:
            sorted_scores = ScoreModel.sum_teams_scores_by_months_id(current_month.id)
        except:
            return {"message": ERROR_GETTING_OBJECTS.format("Score")}, 500

        if not sorted_scores:
            return {"message": ERROR_GETTING_OBJECTS.format("Score")}, 500

        cls.__updates_winners(prize, sorted_scores, total_prize_value)

    @classmethod
    def __updates_winners(
        cls,
        prize: PrizeModel,
        sorted_scores: List[ScoreModel],
        total_prize_value: Decimal,
    ):

        # Deletes the winners by the type of prize if they exists
        try:
            winners_to_delete = WinnerModel.find_by_prizes_id(prize.id)
        except:
            return {"message": ERROR_GETTING_OBJECT.format(Winner.__name__)}, 500

        first_object = True
        for winner_to_delete in winners_to_delete:
            try:
                winner_to_delete.delete_from_db()
            except:
                return {"message": ERROR_DELETING_OBJECT.format(Winner.__name__)}, 500

            if first_object:
                first_object = False
                try:
                    print("reset sequence: {}".format(winner_to_delete.id))
                    WinnerModel.reset_sequence(winner_to_delete.id)
                except:
                    return {
                        "message": ERROR_UPDATING_OBJECT.format(Winner.__name__)
                    }, 500

        # Inserts the winners, their prize value according to the amount of people who paid the monthly fee, their places and prize type
        place = 1
        for score in sorted_scores:
            winner = WinnerModel()
            winner.prizes_id = prize.id
            winner.teams_id = score.teams_id
            winner.place = place

            if place == 1:
                winner.prize_value = (
                    (total_prize_value * prize.first_place_percentage) / 100
                ).quantize(Decimal(".01"), rounding=ROUND_UP)
                print("1st:{}".format(winner))
            elif place == 2:
                winner.prize_value = (
                    (total_prize_value * prize.second_place_percentage) / 100
                ).quantize(Decimal(".01"))
                print("2nd:{}".format(winner))
            elif place == 3:
                winner.prize_value = (
                    (total_prize_value * prize.tird_place_percentage) / 100
                ).quantize(Decimal(".01"))
                print("3rd:{}".format(winner))
            elif place == 4:
                winner.prize_value = (
                    (total_prize_value * prize.fourth_place_percentage) / 100
                ).quantize(Decimal(".01"))
                print("4th:{}".format(winner))

            try:
                winner.save_to_db()
            except:
                return {"message": ERROR_INSERTING_OBJECT.format(Winner.__name__)}, 500

            if place == 4:
                break

            place += 1
