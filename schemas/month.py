from marshmallow import fields, ValidationError
from app import ma
from models.month import MonthModel


def validate_tax(tax):
    if tax <= 0:
        raise ValidationError("The tax must be greater than R$ 0,00.")


class MonthSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MonthModel
        dump_only = (
            "id",
            "created_at",
            "updated_at",
        )
        load_instance = True
        ordered = True

    tax = fields.Decimal(as_string=True, required=True, validate=validate_tax)

    prizes = ma.Nested(
        "PrizeSchema",
        many=True,
        only=(
            "id",
            "name",
        ),
    )
    rounds = ma.Nested(
        "RoundSchema",
        many=True,
        only=(
            "id",
            "round_number",
            "awarded",
        ),
    )
    payments = ma.Nested(
        "PaymentSchema",
        many=True,
        only=(
            "id",
            "team.id",
            "team.name",
            "amount",
        ),
    )
