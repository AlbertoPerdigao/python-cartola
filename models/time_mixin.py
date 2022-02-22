from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr
from app import db


class TimeMixin(object):
    @declared_attr
    def created_at(cls):
        return db.Column(db.DateTime, server_default=func.now(), nullable=False)

    @declared_attr
    def updated_at(cls):
        return db.Column(
            db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
        )

    # This format inserts these fields on top of other columns at the table creation
    # created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    # updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
