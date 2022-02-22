from marshmallow import fields, ValidationError
from app import ma
from models.payment import PaymentModel

# from schemas.team import TeamSchema
# from schemas.month import MonthSchema


def validate_amount(amount):
    if amount <= 0:
        raise ValidationError("Amount must be greater than R$ 0,00.")


class PaymentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PaymentModel
        dump_only = (
            "id",
            "created_at",
            "updated_at",
        )
        load_only = (
            "months_id",
            "teams_id",
        )
        load_instance = True
        include_fk = True
        ordered = True

    amount = fields.Decimal(as_string=True, required=True, validate=validate_amount)

    month = ma.Nested(
        "MonthSchema",
        only=(
            "id",
            "name",
            "year",
        ),
    )
    team = ma.Nested(
        "TeamSchema",
        only=(
            "id",
            "name",
        ),
    )
    # month = ma.Nested(lambda: MonthSchema, only=("id", "name", "year",))
    # team = ma.Nested(lambda: TeamSchema, only=("id", "name",))
