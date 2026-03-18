# app/domain/user.py
from sqlalchemy import Column, BigInteger, String, Boolean, TIMESTAMP
from app.core.database import Base


class User(Base):
    __tablename__ = "usuario"

    cod_usuario = Column(BigInteger, primary_key=True, index=True)
    nome = Column(String)
    login = Column(String, unique=True, index=True)
    email = Column(String)
    senha_hash = Column(String)
    perfil = Column(String)
    ativo = Column(Boolean)