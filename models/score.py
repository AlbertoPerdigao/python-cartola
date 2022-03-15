from decimal import Decimal
from typing import Dict, List

from flask import session
from models.month import MonthModel
from models.time_mixin import TimeMixin
from app import db


class ScoreModel(TimeMixin, db.Model):
    __tablename__ = "scores"

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Numeric(5, 2), nullable=False)

    teams_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    team = db.relationship("TeamModel", back_populates="scores")
    rounds_id = db.Column(db.Integer, db.ForeignKey("rounds.id"), nullable=False)
    round = db.relationship("RoundModel", back_populates="scores")

    def __repr__(self) -> str:
        return "<Score id:{}, value:{}, teams_id:{}, rounds_id:{}>".format(
            self.id, self.value, self.teams_id, self.rounds_id
        )

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
    def find_by_team_slug_round_number_year(
        cls, team_slug: int, round_number: int, year: int
    ) -> "ScoreModel":
        from models.round import RoundModel
        from models.team import TeamModel
        from models.month import MonthModel

        return (
            cls.query.join(RoundModel)
            .join(MonthModel)
            .join(TeamModel)
            .where(
                RoundModel.round_number == round_number,
                TeamModel.slug == team_slug,
                MonthModel.year == year,
            )
            .first()
        )

    @classmethod
    def find_by_rounds_id(cls, rounds_id: int) -> List["ScoreModel"]:
        return cls.query.filter_by(rounds_id=rounds_id).all()

    @classmethod
    def find_by_teams_id(cls, teams_id: int) -> List["ScoreModel"]:
        return cls.query.filter_by(teams_id=teams_id).all()

    @classmethod
    def find_by_teams_id_rounds_id(
        cls, teams_id: int, rounds_id: int
    ) -> List["ScoreModel"]:
        return cls.query.filter_by(teams_id=teams_id, rounds_id=rounds_id).all()

    @classmethod
    def find_all_by_months_id(cls, months_id: int) -> List["ScoreModel"]:
        from models.round import RoundModel

        return (
            cls.query.join(RoundModel).filter(RoundModel.months_id == months_id).all()
        )

    @classmethod
    def sum_teams_scores_by_months_id(cls, months_id: int) -> List["ScoreModel"]:
        from models.round import RoundModel
        from sqlalchemy.sql import func, desc

        scores = (
            db.session.query(func.sum(cls.value).label("value"), cls.teams_id)
            .join(RoundModel)
            .where(RoundModel.months_id == months_id)
            .group_by(cls.teams_id)
            .order_by(desc(func.sum(cls.value).label("value")), desc(cls.teams_id))
            .all()
        )
        scores_list = list()
        for score in scores:
            sm = ScoreModel()
            sm.value = score.value
            sm.teams_id = score.teams_id
            scores_list.append(sm)

        return scores_list

    @classmethod
    def sum_teams_scores_by_list_months_id(
        cls, months_ids: List[int]
    ) -> List["ScoreModel"]:
        from models.round import RoundModel
        from sqlalchemy.sql import func, desc

        scores = (
            db.session.query(func.sum(cls.value).label("value"), cls.teams_id)
            .join(RoundModel)
            .where(RoundModel.months_id.in_(months_ids))
            .group_by(cls.teams_id)
            .order_by(desc(func.sum(cls.value).label("value")), desc(cls.teams_id))
            .all()
        )
        scores_list = list()
        for score in scores:
            sm = ScoreModel()
            sm.value = score.value
            sm.teams_id = score.teams_id
            scores_list.append(sm)

        return scores_list

    @classmethod
    def find_all_by_year(cls, year: int) -> List["ScoreModel"]:
        from models.round import RoundModel
        from models.month import MonthModel

        return (
            cls.query.join(RoundModel)
            .join(MonthModel)
            .filter(MonthModel.year == year)
            .all()
        )
