from sqlalchemy import Column, Integer, String

from app.core.database import Base


class FieldType(Base):
    __tablename__ = "tipo_campo"

    cod_tipo_campo = Column(Integer, primary_key=True, index=True)
    tipo_campo = Column(String(255), nullable=False, unique=True)
