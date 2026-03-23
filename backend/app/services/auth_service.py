# app/services/auth_service.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.domain.user_role import UserRole
from app.repositories.user_repository import UserRepository


class AuthService:
    @staticmethod
    def _map_role(perfil: str) -> str:
        try:
            return UserRole(perfil).label
        except ValueError:
            return perfil

    @staticmethod
    def authenticate_user(db: Session, identifier: str, password: str):
        user = UserRepository.get_by_login_or_email(db, identifier)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário ou senha inválidos",
            )

        if not verify_password(password, user.senha_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário ou senha inválidos",
            )

        if not user.ativo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário inativo",
            )

        return user

    @staticmethod
    def login(db: Session, identifier: str, password: str):
        user = AuthService.authenticate_user(db, identifier, password)
        token = create_access_token(
            data={
                "sub": str(user.cod_usuario),
                "login": user.login,
                "role": user.perfil,
            }
        )

        return {
            "id": user.cod_usuario,
            "name": user.nome,
            "login": user.login,
            "email": user.email,
            "role": AuthService._map_role(user.perfil),
            "active": user.ativo,
            "token": token,
            "access_token": token,
            "token_type": "bearer",
        }
