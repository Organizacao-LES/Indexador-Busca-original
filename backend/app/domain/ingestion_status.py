from sqlalchemy import Column, Integer, String

from app.core.database import Base


class IngestionStatus(Base):
    __tablename__ = "status_ingestao"

    cod_status_ingestao = Column(Integer, primary_key=True, index=True)
    estado_ingestao = Column(String(255), nullable=False, unique=True)
