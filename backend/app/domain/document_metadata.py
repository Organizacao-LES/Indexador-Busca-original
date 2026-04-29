from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func

from app.core.database import Base


class DocumentMetadata(Base):
    __tablename__ = "documento_metadado"
    __table_args__ = (
        UniqueConstraint("cod_documento", name="uq_documento_metadado_documento"),
    )

    cod_documento_metadado = Column(Integer, primary_key=True, index=True)
    cod_documento = Column(Integer, ForeignKey("documento.cod_documento"), nullable=False, index=True)
    autor = Column(String(255), nullable=True)
    tipo_documento = Column(String(100), nullable=True)
    nome_arquivo_original = Column(String(255), nullable=False)
    mime_type = Column(String(255), nullable=False)
    tamanho_bytes = Column(Integer, nullable=False, default=0)
    hash_arquivo = Column(String(64), nullable=False)
    metadados_extras = Column(Text, nullable=True)
    criado_em = Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
    atualizado_em = Column(DateTime(timezone=False), onupdate=func.now())
