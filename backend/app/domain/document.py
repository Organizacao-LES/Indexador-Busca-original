# app/domain/document.py
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func

from app.core.database import Base


class Document(Base):
    __tablename__ = "documento"

    cod_documento = Column(Integer, primary_key=True, index=True)
    cod_categoria = Column(Integer, ForeignKey("categoria_documento.cod_categoria"), nullable=False)
    titulo = Column(String(255), nullable=False)
    tipo = Column(String(255), nullable=False)
    data_publicacao = Column(DateTime(timezone=False), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)
    cod_usuario_criador = Column(Integer, ForeignKey("usuario.cod_usuario"), nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
