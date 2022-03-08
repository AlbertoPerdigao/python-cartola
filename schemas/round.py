from app import ma
from models.round import RoundModel


class RoundSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RoundModel
        dump_only = (
            "id",
            "created_at",
            "updated_at",
        )
        load_only = ("months_id",)
        load_instance = True
        include_fk = True
        ordered = True

    month = ma.Nested(
        "MonthSchema",
        only=(
            "id",
            "name",
            "year",
        ),
    )
    prize = ma.Nested("PrizeSchema", only=("id", "name"))
