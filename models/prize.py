from turtle import st
from typing import List
from models.time_mixin import TimeMixin
from models.winner import WinnerModel

# from models.month import MonthModel
from app import db


class PrizeModel(TimeMixin, db.Model):
    __tablename__ = "prizes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    total_prize_percentage = db.Column(db.Numeric(7, 2), nullable=False)
    first_place_percentage = db.Column(db.Numeric(7, 2), nullable=False)
    second_place_percentage = db.Column(db.Numeric(7, 2), nullable=False)
    tird_place_percentage = db.Column(db.Numeric(7, 2), nullable=False)
    fourth_place_percentage = db.Column(db.Numeric(7, 2), nullable=False)

    months_id = db.Column(db.Integer, db.ForeignKey("months.id"), nullable=False)
    month = db.relationship("MonthModel", back_populates="prizes")
    rounds_id = db.Column(db.Integer, db.ForeignKey("rounds.id"), nullable=True)
    round = db.relationship("RoundModel", back_populates="prize")
    winners = db.relationship("WinnerModel", back_populates="prize", lazy="dynamic")

    def __repr__(self) -> str:
        return "<Prize id:{}, name:{}, total_prize_percentage:{}, first_place_percentage:{}, second_place_percentage:{}, tird_place_percentage:{}, fourth_place_percentage:{}, months_id:{}, rounds_id:{} >".format(
            self.id,
            self.name,
            self.total_prize_percentage,
            self.first_place_percentage,
            self.second_place_percentage,
            self.tird_place_percentage,
            self.fourth_place_percentage,
            self.months_id,
            self.rounds_id,
        )

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, id: int) -> "PrizeModel":
        return cls.query.get(id)

    @classmethod
    def find_by_name_months_id(cls, name: str, months_id: int) -> "PrizeModel":
        return cls.query.filter_by(name=name, months_id=months_id).first()

    @classmethod
    def find_by_months_id(cls, months_id: int) -> List["PrizeModel"]:
        return cls.query.filter_by(months_id=months_id).all()

    @classmethod
    def find_by_rounds_id(cls, rounds_id: int, name: str) -> "PrizeModel":
        return cls.query.filter_by(rounds_id=rounds_id, name=name).first()

    @classmethod
    def find_by_name(cls, name: str, year: int) -> List["PrizeModel"]:
        from models.month import MonthModel

        return (
            cls.query.join(MonthModel)
            .filter(MonthModel.year == year, cls.name == name)
            .all()
        )

    @classmethod
    def find_all_by_year(cls, year: int) -> List["PrizeModel"]:
        from models.month import MonthModel

        return cls.query.join(MonthModel).filter(MonthModel.year == year).all()
