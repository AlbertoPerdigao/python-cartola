from app import ma
from models.team import TeamModel


class TeamSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TeamModel
        dump_only = (
            "id",
            "created_at",
            "updated_at",
        )
        load_instance = True
        ordered = True

    winners = ma.Nested(
        "WinnerSchema", many=True, only=("prizes_id", "place", "prize_value", "prize")
    )
    payments = ma.Nested(
        "PaymentSchema",
        many=True,
        only=("month.id", "month.name", "month.year", "amount"),
    )
