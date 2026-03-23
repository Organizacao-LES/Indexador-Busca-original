from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, constr

from app.domain.user_role import UserRole


class UserBase(BaseModel):
    nome: str = constr(min_length=1, max_length=255)
    login: str = constr(min_length=1, max_length=100)
    email: EmailStr
    perfil: UserRole = UserRole.USER
    ativo: bool = True


class UserCreate(UserBase):
    senha: str = constr(min_length=8)


class UserUpdate(BaseModel):
    nome: str | None = constr(min_length=1, max_length=255)
    login: str | None = constr(min_length=1, max_length=100)
    email: EmailStr | None = None
    perfil: UserRole | None = None
    ativo: bool | None = None
    senha: str | None = constr(min_length=8)


class UserResponse(UserBase):
    cod_usuario: int
    criado_em: datetime
    atualizado_em: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
