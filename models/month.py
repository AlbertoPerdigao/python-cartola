from typing import List
from models.time_mixin import TimeMixin
from models.round import RoundModel
from models.prize import PrizeModel
from app import db


class MonthModel(TimeMixin, db.Model):
    __tablename__ = "months"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    tax = db.Column(db.Numeric(7, 2), nullable=False)

    rounds = db.relationship("RoundModel", back_populates="month", lazy="dynamic")
    payments = db.relationship("PaymentModel", back_populates="month", lazy="dynamic")
    prizes = db.relationship("PrizeModel", back_populates="month", lazy="dynamic")

    def __repr__(self) -> str:
        return "<Month id:{}, name:{}, year:{}, tax:{}>".format(
            self.id, self.name, self.year, self.tax
        )

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, id: int) -> "MonthModel":
        return cls.query.get(id)

    @classmethod
    def find_by_name_year(cls, name: str, year: int) -> "MonthModel":
        return cls.query.filter_by(name=name, year=year).first()

    @classmethod
    def find_by_round_number_year(cls, round_number: int, year: int) -> "MonthModel":
        from models.round import RoundModel
        return cls.query.with_entities(MonthModel).join(RoundModel).where(MonthModel.year == year, RoundModel.round_number == round_number).first()

    @classmethod
    def find_all_by_year(cls, year: int) -> List["MonthModel"]:
        return cls.query.filter_by(year=year).all()
