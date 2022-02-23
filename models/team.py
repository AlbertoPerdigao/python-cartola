from typing import List
from models.time_mixin import TimeMixin
from models.payment import PaymentModel
from models.score import ScoreModel
from app import db


class TeamModel(TimeMixin, db.Model):
    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    slug = db.Column(db.String(128), nullable=False)
    id_tag = db.Column(db.String(128), nullable=False)
    url_escudo_png = db.Column(db.String(255), nullable=False)
    player_name = db.Column(db.String(128), nullable=False)

    winners = db.relationship("WinnerModel", back_populates="team", lazy="dynamic")
    payments = db.relationship("PaymentModel", back_populates="team", lazy="dynamic")
    scores = db.relationship("ScoreModel", back_populates="team", lazy="dynamic")

    def __repr__(self) -> str:
        return "<Team id:{}, name:{}, active:{}, slug:{}, id_tag:{}, url_escudo_png:{}, player_name:{}>".format(
            self.id,
            self.name,
            self.active,
            self.slug,
            self.id_tag,
            self.url_escudo_png,
            self.player_name,
        )

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, id: int) -> "TeamModel":
        return cls.query.get(id)

    @classmethod
    def find_by_name(cls, name: str) -> "TeamModel":
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_all(cls) -> List["TeamModel"]:
        return cls.query.all()
