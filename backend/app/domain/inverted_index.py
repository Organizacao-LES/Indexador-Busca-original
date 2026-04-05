from sqlalchemy import Column, ForeignKey, Integer

from app.core.database import Base


class InvertedIndex(Base):
    __tablename__ = "indice_invertido"

    cod_indice_invertido = Column(Integer, primary_key=True, index=True)
    cod_termo = Column(Integer, ForeignKey("termo.cod_termo"), nullable=False)
    cod_campo_documento = Column(
        Integer,
        ForeignKey("campo_documento.cod_campo_documento"),
        nullable=False,
    )
    tf = Column(Integer, nullable=False)
    posicao_inicial = Column(Integer, nullable=False)
