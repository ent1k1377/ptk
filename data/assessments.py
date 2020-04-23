import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Assessment(SqlAlchemyBase):
    __tablename__ = 'assessments'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    assessment = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    id_user = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    id_teacher = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    subject = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    # created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
