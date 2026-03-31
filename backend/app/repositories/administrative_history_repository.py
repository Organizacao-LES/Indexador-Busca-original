from sqlalchemy.orm import Session

from app.domain.administrative_history import AdministrativeHistory


class AdministrativeHistoryRepository:
    @staticmethod
    def create(db: Session, history: AdministrativeHistory) -> AdministrativeHistory:
        db.add(history)
        db.commit()
        db.refresh(history)
        return history

    @staticmethod
    def list_recent(db: Session, limit: int = 100) -> list[AdministrativeHistory]:
        return (
            db.query(AdministrativeHistory)
            .order_by(
                AdministrativeHistory.criado_em.desc(),
                AdministrativeHistory.cod_historico_administrativo.desc(),
            )
            .limit(limit)
            .all()
        )
