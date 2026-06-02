from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, func

from app.core.database import Base


class IngestionHistory(Base):
    __tablename__ = "historico_ingestao"

    cod_historico_ingestao = Column(Integer, primary_key=True, index=True)
    cod_usuario = Column(Integer, ForeignKey("usuario.cod_usuario"), nullable=False)
    cod_documento = Column(Integer, ForeignKey("documento.cod_documento"), nullable=False)
    cod_status_ingestao = Column(Integer, ForeignKey("status_ingestao.cod_status_ingestao"), nullable=False)
    tipo_ingestao = Column(String(20), nullable=False)
    mensagem_erro = Column(String(255), nullable=True)
    tempo_processamento_ms = Column(Numeric(19, 0), nullable=True)
    criado_em = Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
