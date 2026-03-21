from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, constr


class UserBase(BaseModel):
    nome: str = constr(min_length=1, max_length=255)
    login: str = constr(min_length=1, max_length=100)
    email: EmailStr
    perfil: str = constr(min_length=1, max_length=50)
    ativo: bool = True


class UserCreate(UserBase):
    senha: str = constr(min_length=8)


class UserUpdate(BaseModel):
    nome: str | None = constr(min_length=1, max_length=255)
    login: str | None = constr(min_length=1, max_length=100)
    email: EmailStr | None = None
    perfil: str | None = constr(min_length=1, max_length=50)
    ativo: bool | None = None
    senha: str | None = constr(min_length=8)


class UserResponse(UserBase):
    cod_usuario: int
    criado_em: datetime
    atualizado_em: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
