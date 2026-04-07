from sqlalchemy import Column, ForeignKey, Integer, Text

from app.core.database import Base


class DocumentField(Base):
    __tablename__ = "campo_documento"

    cod_campo_documento = Column(Integer, primary_key=True, index=True)
    cod_historico_documento = Column(
        Integer,
        ForeignKey("historico_documento.cod_historico_documento"),
        nullable=False,
    )
    cod_tipo_campo = Column(Integer, ForeignKey("tipo_campo.cod_tipo_campo"), nullable=False)
    conteudo = Column(Text, nullable=False)
