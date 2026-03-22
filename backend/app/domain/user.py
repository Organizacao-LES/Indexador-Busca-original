# app/domain/user.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    func,
)
from app.core.database import Base


class User(Base):
    __tablename__ = "usuario"

    cod_usuario = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    login = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    perfil = Column(String(50), nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    criado_em = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())