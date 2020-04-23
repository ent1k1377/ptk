import sqlalchemy
from .db_session import SqlAlchemyBase


class numberSubject(SqlAlchemyBase):
    __tablename__ = 'number_subject'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    subject = sqlalchemy.Column(sqlalchemy.String, nullable=True)
