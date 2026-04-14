from datetime import datetime

from sqlalchemy.orm import Session

from app.domain.notification import Notification


class NotificationRepository:
    @staticmethod
    def list_for_user(
        db: Session,
        user_id: int,
        *,
        limit: int = 20,
        only_unread: bool = False,
    ) -> list[Notification]:
        query = db.query(Notification).filter(Notification.cod_usuario == user_id)
        if only_unread:
            query = query.filter(Notification.lida.is_(False))
        return (
            query.order_by(Notification.criada_em.desc(), Notification.cod_notificacao.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_for_user(db: Session, notification_id: int, user_id: int) -> Notification | None:
        return (
            db.query(Notification)
            .filter(
                Notification.cod_notificacao == notification_id,
                Notification.cod_usuario == user_id,
            )
            .first()
        )

    @staticmethod
    def exists_dedup(db: Session, user_id: int, dedup_key: str) -> bool:
        return (
            db.query(Notification.cod_notificacao)
            .filter(
                Notification.cod_usuario == user_id,
                Notification.chave_dedupe == dedup_key,
            )
            .first()
            is not None
        )

    @staticmethod
    def create(db: Session, notification: Notification) -> Notification:
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def unread_count(db: Session, user_id: int) -> int:
        return (
            db.query(Notification)
            .filter(Notification.cod_usuario == user_id, Notification.lida.is_(False))
            .count()
        )

    @staticmethod
    def mark_read(db: Session, notification: Notification) -> Notification:
        if not notification.lida:
            notification.lida = True
            notification.lida_em = datetime.utcnow()
            db.commit()
            db.refresh(notification)
        return notification

    @staticmethod
    def mark_all_read(db: Session, user_id: int) -> int:
        updated = (
            db.query(Notification)
            .filter(Notification.cod_usuario == user_id, Notification.lida.is_(False))
            .update(
                {
                    Notification.lida: True,
                    Notification.lida_em: datetime.utcnow(),
                },
                synchronize_session=False,
            )
        )
        db.commit()
        return updated
