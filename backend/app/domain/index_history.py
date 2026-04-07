from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, func

from app.core.database import Base


class IndexHistory(Base):
    __tablename__ = "historico_indexacao"

    cod_historico_indexacao = Column(Integer, primary_key=True, index=True)
    cod_historico_documento = Column(
        Integer,
        ForeignKey("historico_documento.cod_historico_documento"),
        nullable=False,
    )
    tempo_indexacao_ms = Column(Numeric(19, 0), nullable=False, default=0)
    mensagem_erro = Column(String(255), nullable=True)
    criado_em = Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
