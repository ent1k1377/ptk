import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin


class Teacher(SqlAlchemyBase, UserMixin):
    __tablename__ = 'teachers'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    id_users = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    subjects = sqlalchemy.Column(sqlalchemy.String, nullable=True)

