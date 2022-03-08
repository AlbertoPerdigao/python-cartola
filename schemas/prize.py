from marshmallow import fields, ValidationError
from app import ma
from models.prize import PrizeModel


def validate_percentage(percentage):
    if percentage < 0:
        raise ValidationError("The percentage must be equal or greater than 0%.")


class PrizeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PrizeModel
        dump_only = (
            "id",
            "created_at",
            "updated_at",
        )
        load_only = (
            "months_id",
            "rounds_id",
        )
        load_instance = True
        include_fk = True
        ordered = True

    total_prize_percentage = fields.Decimal(
        as_string=True, required=True, validate=validate_percentage
    )
    first_place_percentage = fields.Decimal(
        as_string=True, required=True, validate=validate_percentage
    )
    second_place_percentage = fields.Decimal(
        as_string=True, required=True, validate=validate_percentage
    )
    tird_place_percentage = fields.Decimal(
        as_string=True, required=True, validate=validate_percentage
    )
    fourth_place_percentage = fields.Decimal(
        as_string=True, required=True, validate=validate_percentage
    )

    winners = ma.Nested(
        "WinnerSchema",
        many=True,
        only=(
            "id",
            "place",
            "prize_value",
            "team",
        ),
    )
    month = ma.Nested(
        "MonthSchema",
        only=(
            "id",
            "name",
            "year",
            "tax",
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
