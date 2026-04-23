import datetime
import sqlalchemy as sa
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)   # Уникальный идентификатор пользователя
    nickname = sa.Column(sa.String, nullable=False, unique=True)  # Имя пользователя
    about = sa.Column(sa.String, nullable=True)  # Описание пользователя
    email = sa.Column(sa.String, index=True, unique=True, nullable=False)  # Адрес электронной почты
    hashed_password = sa.Column(sa.String, nullable=False)  # Зашифрованный пароль пользователя
    avatar = sa.Column(sa.String, nullable=True)  # путь к файлу аватарки
    created_date = sa.Column(sa.DateTime, default=datetime.datetime.now)  # Дата создания пользователя

    reviews = orm.relationship("Review", back_populates="author")
class Review(SqlAlchemyBase):
    __tablename__ = "Reviews"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    title = sa.Column(sa.String, nullable=False)
    content = sa.Column(sa.Text, nullable=False)
    rating = sa.Column(sa.Integer, nullable=False)
    category = sa.Column(sa.String, nullable=False)
    created_date = sa.Column(sa.DateTime, default=datetime.datetime.now)

    author_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    author = orm.relationship("User")

    lat = sa.Column(sa.Float, nullable=True)
    lon = sa.Column(sa.Float, nullable=True)
    address = sa.Column(sa.String, nullable=True)
