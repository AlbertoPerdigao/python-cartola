from typing import List
from app import db
from models.time_mixin import TimeMixin
from models.month import MonthModel


class PaymentModel(TimeMixin, db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(7, 2), nullable=False)

    teams_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    team = db.relationship("TeamModel", back_populates="payments")
    months_id = db.Column(db.Integer, db.ForeignKey("months.id"), nullable=False)
    month = db.relationship("MonthModel", back_populates="payments")

    def __repr__(self) -> str:
        return "<Payment id:{}, amount:{}, teams_id:{}, months_id:{}, month:{}>".format(
            self.id, self.amount, self.teams_id, self.months_id, self.month
        )

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, id: int) -> "PaymentModel":
        return cls.query.get(id)
   
    @classmethod
    def find_by_team_id_month_id(cls, teams_id: int, months_id: int) -> "PaymentModel":
        return cls.query.filter_by(teams_id=teams_id, months_id=months_id).first()

    @classmethod
    def find_all_by_months_id(cls, months_id: int) -> "PaymentModel":
        return cls.query.filter_by(months_id=months_id).all()

    @classmethod
    def find_all_by_year(cls, year: int) -> List["PaymentModel"]:
        from models.team import TeamModel

        payments_list = (
            cls.query.join(MonthModel)
            .join(TeamModel)
            .filter(MonthModel.year == year)
            .all()
        )
        return payments_list
