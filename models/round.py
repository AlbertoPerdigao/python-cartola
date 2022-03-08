from typing import List
from models.time_mixin import TimeMixin
from app import db


class RoundModel(TimeMixin, db.Model):
    __tablename__ = "rounds"

    id = db.Column(db.Integer, primary_key=True)
    round_number = db.Column(db.Integer, nullable=False)
    awarded = db.Column(db.Boolean, nullable=False)

    months_id = db.Column(db.Integer, db.ForeignKey("months.id"), nullable=False)
    month = db.relationship("MonthModel", back_populates="rounds")
    scores = db.relationship("ScoreModel", back_populates="round", lazy="dynamic")
    prize = db.relationship("PrizeModel", back_populates="round", lazy="dynamic")  # 1:1

    def __repr__(self) -> str:
        return "<Round id:{}, round_number:{}, awarded:{}, months_id:{}>".format(
            self.id, self.round_number, self.awarded, self.months_id
        )

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, id: int) -> "RoundModel":
        return cls.query.get(id)

    @classmethod
    def find_rounds_by_year(cls, months_id: int) -> List[int]:
        from models.month import MonthModel

        subquery = (
            MonthModel.query.with_entities(MonthModel.year)
            .where(MonthModel.id == months_id)
            .subquery("subquery")
        )
        rounds = (
            cls.query.with_entities(cls.round_number)
            .join(MonthModel)
            .where(MonthModel.year == subquery.c.year)
            .all()
        )
        return list(round[0] for round in rounds)

    @classmethod
    def find_all_by_year(cls, year: int) -> List["RoundModel"]:
        from models.month import MonthModel

        return cls.query.join(MonthModel).filter(MonthModel.year == year).all()
