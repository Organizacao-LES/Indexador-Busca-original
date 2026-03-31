from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from app.core.database import Base

class AdministrativeHistory(Base):
    __tablename__ = "historico_administrativo"

    cod_historico_administrativo = Column(Integer, primary_key=True, index=True)
    cod_usuario = Column(Integer, ForeignKey("usuario.cod_usuario"), nullable=False)
    descricao = Column(String(255), nullable=False)
    tipo_acao = Column(String(255), nullable=False)
    criado_em = Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
    entidade_tipo = Column(String(255), nullable=False)
    cod_entidade = Column(Integer, nullable=False)
