import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Post(SqlAlchemyBase):
    __tablename__ = 'su'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    headline = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    pathPict = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    id_user = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    position = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default='')
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
