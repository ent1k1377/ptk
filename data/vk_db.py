import sqlalchemy
from .db_session import SqlAlchemyBase


class VkDb(SqlAlchemyBase):
    __tablename__ = 'vk_db'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    id_dialog = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    group = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

