from flask_restful import Resource
from flask import request
from models.score import ScoreModel
from models.team import TeamModel
from models.month import MonthModel
from resources.cartola_api import CartolaApi
from schemas.score import ScoreSchema
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

score_schema = ScoreSchema()
score_list_schema = ScoreSchema(many=True)


class Score(Resource):
    @classmethod
    def get(cls, id: int):
        try:
            score = ScoreModel.find_by_id(id)
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if score:
            return score_schema.dump(score)

        return {"message": OBJECT_NOT_FOUND.format(cls.__name__)}, 404

    @classmethod
    def post(cls, id: int):
        score_json = request.get_json()
        score = score_schema.load(score_json)  # Validates the fields

        try:
            score_exists = ScoreModel.find_by_teams_id_rounds_id(
                score.teams_id, score.rounds_id
            )
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if score_exists:
            return {"message": OBJECT_ALREADY_EXISTS.format(cls.__name__)}, 400

        try:
            score.save_to_db()
        except:
            return {"message": ERROR_INSERTING_OBJECT.format(cls.__name__)}, 500

        return {"message": OBJECT_CREATED_SUCCESSFULLY.format(cls.__name__)}, 201

    @classmethod
    def put(cls, id: int):
        score_json = request.get_json()
        modified_score = score_schema.load(
            score_json, partial=("teams_id", "rounds_id")
        )  # Validates the fields

        try:
            score = ScoreModel.find_by_id(id)  # find the score to update
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if not score:
            return {"message": OBJECT_NOT_FOUND.format(cls.__name__)}, 404

        score.value = modified_score.value

        try:
            score.save_to_db()
        except:
            return {"message": ERROR_UPDATING_OBJECT.format(cls.__name__)}, 500

        return score_schema.dump(score), 200

    @classmethod
    def delete(cls, id: int):
        try:
            score = ScoreModel.find_by_id(id)
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if score:
            try:
                score.delete_from_db()
                return {
                    "message": OBJECT_DELETED_SUCCESSFULLY.format(cls.__name__)
                }, 200
            except:
                return {"message": ERROR_DELETING_OBJECT.format(cls.__name__)}, 500

        return {"message": OBJECT_NOT_FOUND.format(cls.__name__)}, 404


class ScoreList(Resource):
    @classmethod
    def get(cls, year: int):
        try:
            scores = ScoreModel.find_all_by_year(year)
        except:
            return {"message": ERROR_GETTING_OBJECTS.format(cls.__name__)}, 500

        return {"scores": score_list_schema.dump(scores)}, 200


class ScoreCartolaUpdate:
    @classmethod
    def update_teams_scores(cls, current_round_number: int, current_year: int) -> None:
        # Gets all teams
        try:
            teams = TeamModel.find_all()
        except:
            return {"message": ERROR_GETTING_OBJECTS.format(TeamModel.__name__)}, 500

        # Finds the round id by round number and year
        try:
            current_month = MonthModel.find_by_round_number_year(
                current_round_number, current_year
            )
        except:
            return {"message": ERROR_GETTING_OBJECT.format(MonthModel.__name__)}, 500

        month_rounds = current_month.rounds

        round_id = 0
        for round in month_rounds:
            if round.round_number == current_round_number:
                round_id = round.id
                break

        # For each team, updates the score based on the Cartola FC api;
        # if the score is not already created for the current round, creates it

        for team in teams:
            # cartola_team = CartolaApi.get_cartola_team_by_team_id_tag(team.id_tag)
            # cartola_team_score_value = cartola_team["pontos"]
            # cartola_team_score_cartoletas = cartola_team["patrimonio"]
            ### remove this code snippet when Cartola API is working, replacing it with the 3 lines above
            import random, decimal

            cartola_team_score_value = decimal.Decimal(random.randrange(0, 120))
            cartola_team_score_cartoletas = decimal.Decimal(random.randrange(0, 500))
            ###

            try:
                score = ScoreModel.find_by_team_id_tag_round_number_year(
                    team.id_tag, current_round_number, current_year
                )
            except:
                return {
                    "message": ERROR_GETTING_OBJECT.format(MonthModel.__name__)
                }, 500

            if score:
                score.value = cartola_team_score_value
                score.cartoletas = cartola_team_score_cartoletas
            else:
                score = ScoreModel()
                score.value = cartola_team_score_value
                score.cartoletas = cartola_team_score_cartoletas
                score.rounds_id = round_id
                score.teams_id = team.id

            try:
                score.save_to_db()
            except:
                return {
                    "message": ERROR_UPDATING_OBJECT.format(ScoreModel.__name__)
                }, 500
