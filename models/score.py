from typing import List
from models.time_mixin import TimeMixin
from app import db


class ScoreModel(TimeMixin, db.Model):
    __tablename__ = "scores"

    id = db.Column(db.Integer, primary_key=True)    
    points = db.Column(db.Numeric(5, 2), nullable=False)

    teams_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    team = db.relationship("TeamModel", back_populates="scores")
    rounds_id = db.Column(db.Integer, db.ForeignKey("rounds.id"), nullable=False)
    round = db.relationship("RoundModel", back_populates="scores")

    def __repr__(self) -> str:
        return "<Score id:{}, points:{}, teams_id:{}, rounds_id:{}>".format(self.id, self.points, self.teams_id, self.rounds_id)

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, id: int) -> "ScoreModel":
        return cls.query.get(id)

    @classmethod
    def find_by_rounds_id(cls, rounds_id: int) -> "ScoreModel":
        return cls.query.filter_by(rounds_id=rounds_id).all()

    @classmethod
    def find_by_teams_id(cls, teams_id: int) -> "ScoreModel":
        return cls.query.filter_by(teams_id=teams_id).all()

    @classmethod
    def find_by_teams_id_rounds_id(cls, teams_id: int, rounds_id: int) -> "ScoreModel":
        return cls.query.filter_by(teams_id=teams_id, rounds_id=rounds_id).all()
    
    @classmethod
    def find_all_by_months_id(cls, months_id: int) -> List["ScoreModel"]:
        from models.round import RoundModel
        
        return (
            cls.query.join(RoundModel).filter(RoundModel.months_id == months_id)
        )

    @classmethod
    def find_all_by_year(cls, year: int) -> List["ScoreModel"]:
        from models.round import RoundModel
        from models.month import MonthModel

        return (
            cls.query.join(RoundModel).join(MonthModel).filter(MonthModel.year == year)
        )
