# app/repositories/user_repository.py

from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.domain.user import User


class UserRepository:

    @staticmethod
    def get_by_login(db: Session, login: str):
        return db.query(User).filter(User.login == login).first()

    @staticmethod
    def get_by_email(db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_login_or_email(db: Session, identifier: str):
        return (
            db.query(User)
            .filter(or_(User.login == identifier, User.email == identifier))
            .first()
        )

    @staticmethod
    def get_by_id(db: Session, user_id: int):
        return db.query(User).filter(User.cod_usuario == user_id).first()
