from decimal import Decimal, ROUND_UP
from typing import List
from werkzeug.security import safe_str_cmp
from flask import request
from flask_restful import Resource
from models.month import MonthModel
from models.prize import PrizeModel
from models.score import ScoreModel
from models.payment import PaymentModel
from models.winner import WinnerModel
from resources.score import ScoreCartolaUpdate
from resources.cartola_api import CartolaApi
from resources.score import ScoreCartolaUpdate
from app.messages import (
    ERROR_GETTING_OBJECT,
    ERROR_GETTING_OBJECTS,
    ERROR_INSERTING_OBJECT,
    ERROR_UPDATING_OBJECT,
    ERROR_DELETING_OBJECT,
)

RODADA_PREMIADA_PRIZE = "Rodada Premiada"
MES_PRIZE = "Mês"
TURNO_PRIZE = "Turno"
COPA_DA_LIGA_PRIZE = "Copa da Liga"
PATRIMONIO_PRIZE = "Patrimônio"
CAMPEONATO_PRIZE = "Campeonato"
TOTAL_PAYMENTS_TO_UNLOCK_4TH_PLACE = 35
FIRST_PLACE_PERCENTAGE = 50
FIRST_PLACE_PERCENTAGE_UNLOCKED_4TH_PLACE = 40
FOURTH_PLACE_PERCENTAGE = 0
FOURTH_PLACE_PERCENTAGE_UNLOCKED_4TH_PLACE = 10
PATRIMONIO_FIRST_PLACE_PERCENTAGE = 3.33
PATRIMONIO_FIRST_PLACE_PERCENTAGE_UNLOCKED_2TH_PLACE = 2
PATRIMONIO_SECOND_PLACE_PERCENTAGE = 0
PATRIMONIO_SECOND_PLACE_PERCENTAGE_UNLOCKED_2TH_PLACE = 1.33


class WinnerPrizesCalculation(Resource):
    @classmethod
    def get(cls):
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
       
        print("YEAR: {}, ROUND: {}".format(current_year, current_round_number))

        # Updates the teams scores trough the current round an year
        ScoreCartolaUpdate.update_teams_scores(current_round_number, current_year)

        # Campeonato Prize
        msg = cls.__calculates_campeonato_prize_winners(current_year)
        if msg:
            return msg

        # Turno Prize
        cls.__calculates_turno_prize_winners(current_round_number, current_year)

        # Mês, Rodada Premiada and Copa da Liga prizes
        try:
            current_month = MonthModel.find_by_round_number_year(
                current_round_number, current_year
            )
        except:
            return {"message": ERROR_GETTING_OBJECT.format("Month")}, 500

        if not current_month:
            return {"message": ERROR_GETTING_OBJECT.format("Month")}, 500

        # Gets the current month's payment amount
        try:
            payments = PaymentModel.find_all_by_months_id(current_month.id)
        except:
            return {"message": ERROR_GETTING_OBJECTS.format("Payments")}, 500

        total_payments_amount = 0
        for payment in payments:
            total_payments_amount += payment.amount

        unlock_2nd_or_4th_place = True if len(payments) >= TOTAL_PAYMENTS_TO_UNLOCK_4TH_PLACE else False

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
                print("\nPrize:{}".format(COPA_DA_LIGA_PRIZE))

        # Patrimônio Prize
        for prize in current_month.prizes:
            if safe_str_cmp(prize.name, PATRIMONIO_PRIZE):
                cls.__calculates_patrimonio_prize_winners(
                    current_month, total_payments_amount, prize, current_round_number, unlock_2nd_or_4th_place
                )

        return {"message": "Automatic prizes calculation finished with success!"}

    @classmethod
    def __calculates_patrimonio_prize_winners(
        cls,
        current_month: MonthModel,
        total_payments_amount: Decimal,
        prize: PrizeModel,
        current_round_number: int,
        unlock_2nd_place: bool
    ) -> None:
        print("\nPrize: {} - Month: {}".format(PATRIMONIO_PRIZE, current_month.id))

        # The winners will be those who have the highest number of cartoletas and
        # who have not won another prize in the current month

        # Gets the teams scores and cartoletas of the month
        try:
            month_scores = ScoreModel.find_all_by_months_id(current_month.id)
        except:
            return {"message": ERROR_GETTING_OBJECTS.format("Score")}, 500

        if not month_scores:
            return {"message": ERROR_GETTING_OBJECTS.format("Score")}, 500

        # Calculates the team's patrimony
        # The calculation consists of taking the difference between the
        # number of cartoletas from the first and the last rounds of the month

        round_numbers = []
        for month_score in month_scores:
            round_numbers.append(month_score.round.round_number)
        round_numbers = sorted(round_numbers)
        first_round = round_numbers[0]
        last_round = round_numbers[-1]

        teams_patrimony = {}
        for month_score in month_scores:
            if month_score.round.round_number == first_round:
                teams_patrimony[month_score.teams_id] = month_score.cartoletas
        for month_score in month_scores:
            if month_score.round.round_number == last_round:
                teams_patrimony[month_score.teams_id] = (
                    month_score.cartoletas - teams_patrimony[month_score.teams_id]
                )

        sorted_teams_patrimony = sorted(
            teams_patrimony.items(), key=lambda item: item[1], reverse=True
        )        

        # Gets the teams who already have a prize in the current month
        try:
            all_prizes_winners = WinnerModel.find_all_by_months_id(current_month.id)
        except:
            return {"message": ERROR_GETTING_OBJECTS.format("Winner")}, 500

        # This code below is necessary to withdraw the partial winners of the Turno and Campeonato prizes
        awarded_teams_ids = set()
        for winner in all_prizes_winners:
            if (
                safe_str_cmp(winner.prize.name, CAMPEONATO_PRIZE)
                or safe_str_cmp(winner.prize.name, TURNO_PRIZE)
            ) and winner.prize.round.round_number != current_round_number:
                break
            awarded_teams_ids.add(winner.teams_id)

        patrimony_winners = []
        for team in sorted_teams_patrimony:
            if team[0] in awarded_teams_ids:
                continue
            patrimony_winners.append(team)
            if len(patrimony_winners) == 2:
                break

        cls.__updates_prize_places_percentage(unlock_2nd_place, prize)
        
        total_prize_value = round(
            (prize.total_prize_percentage * total_payments_amount) / 100
        )
        
        sorted_scores = []
        for patrimony_winner in patrimony_winners:
            score = ScoreModel()
            score.teams_id = patrimony_winner[0]
            sorted_scores.append(score)

        cls.__updates_winners(prize, sorted_scores, total_prize_value)        

    @classmethod
    def __calculates_campeonato_prize_winners(cls, current_year: int) -> None:
        print("\nPrize: {} - Year: {}".format(CAMPEONATO_PRIZE, current_year))

        # The winners will be those who have the highest number of points in the year

        # Gets the amount of payments of the year
        total_payments_amount = 0
        try:
            payments = PaymentModel.find_all_by_year(current_year)
        except:
            return {"message": ERROR_GETTING_OBJECTS.format("Payments")}, 500

        total_month_payments = list()
        for payment in payments:
            total_payments_amount += payment.amount
            total_month_payments.append(payment.months_id)

        unique_months_ids = list(set(total_month_payments))
        unlock_4th_place = True
        for unique_month_id in unique_months_ids:
            if (
                total_month_payments.count(unique_month_id)
                < TOTAL_PAYMENTS_TO_UNLOCK_4TH_PLACE
            ):
                unlock_4th_place = False
                break

        try:
            prizes = PrizeModel.find_by_name(CAMPEONATO_PRIZE, current_year)
        except:
            return {"message": ERROR_GETTING_OBJECT.format("Prize")}, 500

        if not prizes:
            return {"message": ERROR_GETTING_OBJECT.format("Prize")}, 500

        prize = prizes[0]
        cls.__updates_prize_places_percentage(unlock_4th_place, prize)

        total_prize_value = (
            (prize.total_prize_percentage * total_payments_amount) / 100
        ).quantize(Decimal(".01"))

        # Gets the teams scores of the year
        try:
            sorted_scores = ScoreModel.sum_teams_scores_by_year(current_year)
        except:
            return {"message": ERROR_GETTING_OBJECTS.format("Score")}, 500

        if not sorted_scores:
            return {"message": ERROR_GETTING_OBJECTS.format("Score")}, 500

        cls.__updates_winners(prize, sorted_scores, total_prize_value)

    @classmethod
    def __calculates_turno_prize_winners(
        cls,
        current_round_number: int,
        current_year: int,
    ) -> None:
        print(
            "\nPrize: {} - Shift: {}".format(
                TURNO_PRIZE, 1 if current_round_number <= 19 else 2
            )
        )

        # The winners will be those who have the highest number of points in the current shift
        # The shifts are divided in 2: shift 1 - round 1 to 19 and shift 2 - round 20 to 38

        # Gets the amount of payments for the current shift months
        try:
            months_ids = MonthModel.find_shift_months_ids_by_round_number_year(
                current_round_number, current_year
            )
        except:
            return {"message": ERROR_GETTING_OBJECTS.format("MonthModel")}, 500

        total_payments_amount = 0
        unlock_4th_place_list = list()
        for month_id in months_ids:
            try:
                payments = PaymentModel.find_all_by_months_id(month_id)
            except:
                return {"message": ERROR_GETTING_OBJECTS.format("Payments")}, 500

            for payment in payments:
                total_payments_amount += payment.amount

            unlock_4th_place_list.append(
                True if len(payments) >= TOTAL_PAYMENTS_TO_UNLOCK_4TH_PLACE else False
            )
            unlock_4th_place = False if False in unlock_4th_place_list else True

        # Gets the prize
        try:
            turno_prizes = PrizeModel.find_by_name(TURNO_PRIZE, current_year)
        except:
            return {"message": ERROR_GETTING_OBJECT.format("Prize")}, 500

        for turno_prize in turno_prizes:
            if (
                turno_prize.round.round_number == 19 and current_round_number <= 19
            ) or (turno_prize.round.round_number == 38 and current_round_number > 19):
                prize = turno_prize

        if not prize:
            return {"message": ERROR_GETTING_OBJECT.format("Prize")}, 500

        cls.__updates_prize_places_percentage(unlock_4th_place, prize)

        total_prize_value = (
            (prize.total_prize_percentage * total_payments_amount) / 100
        ).quantize(Decimal(".01"))

        # Gets the scores of the shift
        try:
            sorted_scores = ScoreModel.sum_teams_scores_by_list_months_id(months_ids)
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
            "\nPrize: {} - Month: {} - Round: {}".format(
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

        print("\nPrize: {} - Month: {}".format(prize.name, current_month.id))

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
    ) -> None:
        
        # Deletes the winners by the type of prize if they exists
        try:
            winners_to_delete = WinnerModel.find_by_prizes_id(prize.id)
        except:
            return {"message": ERROR_GETTING_OBJECT.format("Winner")}, 500

        if not winners_to_delete:
            try:                                
                WinnerModel.reset_sequence(0)
            except:
                return {"message": ERROR_UPDATING_OBJECT.format("Winner")}, 500
        else:
            first_object = True
            for winner_to_delete in winners_to_delete:
                try:
                    winner_to_delete.delete_from_db()
                except:
                    return {"message": ERROR_DELETING_OBJECT.format("Winner")}, 500

                if first_object:
                    first_object = False
                    try:
                        # print("reset sequence: {}".format(winner_to_delete.id))
                        WinnerModel.reset_sequence(winner_to_delete.id)
                    except:
                        return {"message": ERROR_UPDATING_OBJECT.format("Winner")}, 500

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
                return {"message": ERROR_INSERTING_OBJECT.format("Winner")}, 500

            if place == 4:
                break

            place += 1

    @classmethod
    def __updates_prize_places_percentage(
        cls, unlock_2nd_or_4th_places: bool, prize: PrizeModel
    ) -> None:
        if safe_str_cmp(prize.name, PATRIMONIO_PRIZE):
            if unlock_2nd_or_4th_places:
                prize.first_place_percentage = (
                    PATRIMONIO_FIRST_PLACE_PERCENTAGE_UNLOCKED_2TH_PLACE
                )
                prize.second_place_percentage = (
                    PATRIMONIO_SECOND_PLACE_PERCENTAGE_UNLOCKED_2TH_PLACE
                )
            else:
                prize.first_place_percentage = PATRIMONIO_FIRST_PLACE_PERCENTAGE
                prize.second_place_percentage = PATRIMONIO_SECOND_PLACE_PERCENTAGE
        else:
            if unlock_2nd_or_4th_places:
                prize.first_place_percentage = FIRST_PLACE_PERCENTAGE_UNLOCKED_4TH_PLACE
                prize.fourth_place_percentage = (
                    FOURTH_PLACE_PERCENTAGE_UNLOCKED_4TH_PLACE
                )
            else:
                prize.first_place_percentage = FIRST_PLACE_PERCENTAGE
                prize.fourth_place_percentage = FOURTH_PLACE_PERCENTAGE

        try:
            prize.save_to_db()
        except:
            return {"message": ERROR_UPDATING_OBJECT.format("Prize")}, 500
