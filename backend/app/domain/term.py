from sqlalchemy import Column, Integer, Numeric, String

from app.core.database import Base


class Term(Base):
    __tablename__ = "termo"

    cod_termo = Column(Integer, primary_key=True, index=True)
    texto_termo = Column(String(255), nullable=False, unique=True)
    df = Column(Numeric(19, 0), nullable=False, default=0)
    idf = Column(Integer, nullable=True)
