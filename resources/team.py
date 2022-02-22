from flask_restful import Resource
from flask import request
from models.team import TeamModel
from schemas.team import TeamSchema
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

team_schema = TeamSchema()
team_list_schema = TeamSchema(many=True)


class Team(Resource):
    @classmethod
    def get(cls, id: int):
        try:
            team = TeamModel.find_by_id(id)
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if team:
            return team_schema.dump(team)

        return {"message": OBJECT_NOT_FOUND.format(cls.__name__)}, 404

    @classmethod
    def post(cls, id: int):
        team_json = request.get_json()
        team = team_schema.load(team_json)  # Validates the fields

        try:
            team_exists = TeamModel.find_by_name(team_json["name"])
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if team_exists:
            return {"message": OBJECT_ALREADY_EXISTS.format(cls.__name__)}, 400

        try:
            team.save_to_db()
        except:
            return {"message": ERROR_INSERTING_OBJECT.format(cls.__name__)}, 500

        return {"message": OBJECT_CREATED_SUCCESSFULLY.format(cls.__name__)}, 201

    @classmethod
    def put(cls, id: int):
        team_json = request.get_json()
        modified_team = team_schema.load(
            team_json, partial=("id_tag", "player_name", "slug", "url_escudo_png")
        )  # Validates the fields / partial -> not required

        try:
            team = TeamModel.find_by_id(id)
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if not team:
            return {"message": OBJECT_NOT_FOUND.format(cls.__name__)}, 404

        team.name = modified_team.name
        team.active = modified_team.active

        try:
            team.save_to_db()
        except:
            return {"message": ERROR_UPDATING_OBJECT.format(cls.__name__)}, 500

        return team_schema.dump(team), 200

    @classmethod
    def delete(cls, id: int):
        try:
            team = TeamModel.find_by_id(id)
        except:
            return {"message": ERROR_GETTING_OBJECT.format(cls.__name__)}, 500

        if team:
            try:
                team.delete_from_db()
                return {
                    "message": OBJECT_DELETED_SUCCESSFULLY.format(cls.__name__)
                }, 200
            except:
                return {"message": ERROR_DELETING_OBJECT.format(cls.__name__)}, 500

        return {"message": OBJECT_NOT_FOUND.format(cls.__name__)}, 404


class TeamList(Resource):
    @classmethod
    def get(cls):
        try:
            teams = TeamModel.find_all()
        except:
            return {"message": ERROR_GETTING_OBJECTS.format(cls.__name__)}, 500

        return {"teams": team_list_schema.dump(teams)}, 200
