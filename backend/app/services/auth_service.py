# app/services/auth_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.user_repository import UserRepository
from app.core.security import verify_password, create_access_token


class AuthService:

    @staticmethod
    def _map_role(perfil: str) -> str:
        return "Administrador" if perfil == "ADMIN" else "Usuário"

    @staticmethod
    def authenticate_user(db: Session, identifier: str, password: str):
        user = UserRepository.get_by_login_or_email(db, identifier)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário ou senha inválidos"
            )

        if not verify_password(password, user.senha_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário ou senha inválidos"
            )

        if not user.ativo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário inativo"
            )

        return user

    @staticmethod
    def login(db: Session, identifier: str, password: str):
        user = AuthService.authenticate_user(db, identifier, password)
        token = create_access_token(
            data={
                "sub": str(user.cod_usuario),
                "login": user.login,
                "role": user.perfil
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
            "token_type": "bearer"
        }
