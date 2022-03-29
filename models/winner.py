from typing import List
from models.time_mixin import TimeMixin
from app import db


class WinnerModel(TimeMixin, db.Model):
    __tablename__ = "winners"

    id = db.Column(db.Integer, primary_key=True)
    place = db.Column(db.Integer, nullable=False)
    prize_value = db.Column(db.Numeric(7, 2), nullable=False)

    teams_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    team = db.relationship("TeamModel", back_populates="winners")
    prizes_id = db.Column(db.Integer, db.ForeignKey("prizes.id"), nullable=False)
    prize = db.relationship("PrizeModel", back_populates="winners")

    def __repr__(self) -> str:
        return "<Winner id:{}, palce:{}, prize_value:{}, teams_id:{}, prizes_id:{}>".format(
            self.id, self.place, self.prize_value, self.teams_id, self.prizes_id
        )

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def reset_sequence(cls, id_sequence: int) -> None:

        if (id_sequence == 0):
            sql = "SELECT (SELECT setval('scm_teste_python.winners_id_seq', id)) FROM scm_teste_python.winners ORDER BY id DESC LIMIT 1;"
        else:            
            sql = "SELECT setval('scm_teste_python.winners_id_seq', {}, FALSE);".format(
                id_sequence
            )
        db.session.execute(sql)

    @classmethod
    def find_by_id(cls, id: int) -> "WinnerModel":
        return cls.query.get(id)

    @classmethod
    def find_by_prizes_id(cls, prizes_id: int) -> "WinnerModel":
        return cls.query.filter_by(prizes_id=prizes_id).all()

    @classmethod
    def find_by_teams_id(cls, teams_id: int) -> "WinnerModel":
        return cls.query.filter_by(teams_id=teams_id).all()

    @classmethod
    def find_by_teams_id_prizes_id(cls, teams_id: int, prizes_id: int) -> "WinnerModel":
        return cls.query.filter_by(teams_id=teams_id, prizes_id=prizes_id).first()

    @classmethod
    def find_by_month_name_year(cls, month_name: int, year: int) -> "WinnerModel":
        from models.prize import PrizeModel
        from models.month import MonthModel

        return (
            cls.query.join(PrizeModel)
            .join(MonthModel)
            .filter(MonthModel.name == month_name, MonthModel.year == year)
            .all()
        )

    @classmethod
    def find_all_by_months_id(cls, months_id: int) -> List["WinnerModel"]:
        from models.prize import PrizeModel

        return (
            cls.query.join(PrizeModel).filter(PrizeModel.months_id == months_id).all()
        )

    @classmethod
    def find_all_by_year(cls, year: int) -> List["WinnerModel"]:
        from models.prize import PrizeModel
        from models.month import MonthModel

        return (
            cls.query.join(PrizeModel)
            .join(MonthModel)
            .filter(MonthModel.year == year)
            .all()
        )
