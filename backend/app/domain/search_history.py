from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text, func

from app.core.database import Base


class SearchHistory(Base):
    __tablename__ = "historico_busca"

    cod_historico_busca = Column(Integer, primary_key=True, index=True)
    cod_usuario = Column(Integer, ForeignKey("usuario.cod_usuario"), nullable=False)
    consulta_texto = Column(Text, nullable=False)
    filtros = Column(String(255), nullable=True)
    quantidade_resultados = Column(Integer, nullable=False, default=0)
    tempo_resposta_ms = Column(Numeric(19, 0), nullable=False, default=0)
    criado_em = Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
