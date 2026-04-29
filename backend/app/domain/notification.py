from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)

from app.core.database import Base


class Notification(Base):
    __tablename__ = "notificacao"
    __table_args__ = (
        UniqueConstraint(
            "cod_usuario",
            "chave_dedupe",
            name="uq_notificacao_usuario_chave_dedupe",
        ),
    )

    cod_notificacao = Column(Integer, primary_key=True, index=True)
    cod_usuario = Column(Integer, ForeignKey("usuario.cod_usuario"), nullable=False, index=True)
    titulo = Column(String(120), nullable=False)
    mensagem = Column(Text, nullable=False)
    tipo = Column(String(30), nullable=False, default="info")
    origem = Column(String(80), nullable=False, default="ifesdoc")
    lida = Column(Boolean, default=False, nullable=False)
    criada_em = Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
    lida_em = Column(DateTime(timezone=False), nullable=True)
    chave_dedupe = Column(String(160), nullable=True)
