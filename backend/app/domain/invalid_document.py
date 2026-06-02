from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from app.core.database import Base


class InvalidDocument(Base):
    __tablename__ = "documentos_invalidos"

    cod_documentos_invalidos = Column(Integer, primary_key=True, index=True)
    cod_usuario = Column(Integer, ForeignKey("usuario.cod_usuario"), nullable=False)
    nome_arquivo = Column(String(255), nullable=False)
    motivo_erro = Column(String(255), nullable=False)
    criado_em = Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
