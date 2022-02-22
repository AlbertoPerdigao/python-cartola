from marshmallow import fields, ValidationError
from app import ma
from models.winner import WinnerModel


def validate_prize_value(prize_value):
    if prize_value <= 0:
        raise ValidationError("The prize value must be greater than 0.")


def validate_place(place):
    if place < 1 or place > 4:
        raise ValidationError("The palce must be between 1 and 4.")


class WinnerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WinnerModel
        dump_only = (
            "id",
            "created_at",
            "updated_at",
        )
        load_only = (
            "prizes_id",
            "teams_id",
        )
        load_instance = True
        include_fk = True

    place = fields.Integer(required=True, validate=validate_place)
    prize_value = fields.Decimal(
        as_string=True, required=True, validate=validate_prize_value
    )
    prize = ma.Nested(
        "PrizeSchema", only=("id", "name", "month.id", "month.name", "month.year")
    )
    team = ma.Nested(
        "TeamSchema",
        only=(
            "id",
            "name",
        ),
    )
