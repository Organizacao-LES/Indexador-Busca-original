from sqlalchemy import Column, Integer, String

from app.core.database import Base


class DocumentCategory(Base):
    __tablename__ = "categoria_documento"

    cod_categoria = Column(Integer, primary_key=True, index=True)
    nome_categoria = Column(String(255), nullable=False, unique=True)
