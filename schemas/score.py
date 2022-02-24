from marshmallow import fields
from app import ma
from models.score import ScoreModel


class ScoreSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ScoreModel
        dump_only = (
            "id",
            "created_at",
            "updated_at",
        )
        load_only = ("teams_id", "rounds_id",)
        load_instance = True
        include_fk = True
        ordered = True

    value = fields.Decimal(as_string=True, required=True)    
    
    team = ma.Nested(
        "TeamSchema",
        only=(
            "id",
            "name",
        ),
    )

    round = ma.Nested(
        "RoundSchema",        
        only=(
            "id",
            "round_number",
            "awarded",
        ),
    )
