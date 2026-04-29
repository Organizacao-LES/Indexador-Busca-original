from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.domain.index_history import IndexHistory
from app.domain.invalid_document import InvalidDocument
from app.domain.notification import Notification
from app.domain.user import User
from app.domain.user_role import UserRole
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.notification_schema import NotificationCreate, NotificationType


class NotificationService:
    def __init__(self, repository: NotificationRepository):
        self.repository = repository

    def to_response(self, notification: Notification) -> dict:
        return {
            "id": notification.cod_notificacao,
            "userId": notification.cod_usuario,
            "title": notification.titulo,
            "message": notification.mensagem,
            "type": notification.tipo,
            "origin": notification.origem,
            "read": notification.lida,
            "createdAt": notification.criada_em,
            "readAt": notification.lida_em,
        }

    def list_for_user(
        self,
        db: Session,
        user: User,
        *,
        limit: int = 20,
        only_unread: bool = False,
    ) -> list[dict]:
        notifications = self.repository.list_for_user(
            db,
            user.cod_usuario,
            limit=limit,
            only_unread=only_unread,
        )
        return [self.to_response(notification) for notification in notifications]

    def unread_count(self, db: Session, user: User) -> int:
        return self.repository.unread_count(db, user.cod_usuario)

    def create_for_user(
        self,
        db: Session,
        *,
        user_id: int,
        title: str,
        message: str,
        type: NotificationType = "info",
        origin: str = "ifesdoc",
        dedup_key: str | None = None,
    ) -> Notification | None:
        if dedup_key and self.repository.exists_dedup(db, user_id, dedup_key):
            return None

        notification = Notification(
            cod_usuario=user_id,
            titulo=title[:120],
            mensagem=message[:2000],
            tipo=type,
            origem=origin[:80],
            chave_dedupe=dedup_key,
        )
        return self.repository.create(db, notification)

    def create_from_payload(
        self,
        db: Session,
        payload: NotificationCreate,
        *,
        origin: str,
    ) -> list[dict]:
        if payload.broadcast:
            users = db.query(User).filter(User.ativo.is_(True)).all()
        else:
            user = UserRepository.get_by_id(db, payload.userId or 0)
            if not user or not user.ativo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuário de destino não encontrado ou inativo.",
                )
            users = [user]

        created: list[Notification] = []
        for user in users:
            notification = self.create_for_user(
                db,
                user_id=user.cod_usuario,
                title=payload.title,
                message=payload.message,
                type=payload.type,
                origin=origin,
            )
            if notification:
                created.append(notification)

        return [self.to_response(notification) for notification in created]

    def mark_read(self, db: Session, user: User, notification_id: int) -> dict:
        notification = self.repository.get_for_user(db, notification_id, user.cod_usuario)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notificação não encontrada.",
            )
        return self.to_response(self.repository.mark_read(db, notification))

    def mark_all_read(self, db: Session, user: User) -> dict:
        return {"updated": self.repository.mark_all_read(db, user.cod_usuario)}

    def active_admins(self, db: Session) -> list[User]:
        return (
            db.query(User)
            .filter(User.ativo.is_(True), User.perfil == UserRole.ADMIN.value)
            .all()
        )

    def notify_admins(
        self,
        db: Session,
        *,
        title: str,
        message: str,
        type: NotificationType = "info",
        origin: str = "ifesdoc-worker",
        dedup_key: str | None = None,
    ) -> int:
        created_count = 0
        for admin in self.active_admins(db):
            notification = self.create_for_user(
                db,
                user_id=admin.cod_usuario,
                title=title,
                message=message,
                type=type,
                origin=origin,
                dedup_key=dedup_key,
            )
            if notification:
                created_count += 1
        return created_count

    def notify_recent_failures(self, db: Session, *, limit: int = 20) -> int:
        created_count = 0

        invalid_documents = (
            db.query(InvalidDocument)
            .order_by(
                InvalidDocument.criado_em.desc(),
                InvalidDocument.cod_documentos_invalidos.desc(),
            )
            .limit(limit)
            .all()
        )
        for invalid_document in invalid_documents:
            created_count += self.notify_admins(
                db,
                title="Documento rejeitado",
                message=(
                    f"{invalid_document.nome_arquivo}: "
                    f"{invalid_document.motivo_erro}"
                ),
                type="warning",
                dedup_key=f"invalid-document:{invalid_document.cod_documentos_invalidos}",
            )

        index_errors = (
            db.query(IndexHistory)
            .filter(IndexHistory.mensagem_erro.isnot(None))
            .order_by(
                IndexHistory.criado_em.desc(),
                IndexHistory.cod_historico_indexacao.desc(),
            )
            .limit(limit)
            .all()
        )
        for index_error in index_errors:
            created_count += self.notify_admins(
                db,
                title="Falha de indexação",
                message=index_error.mensagem_erro or "Erro de indexação registrado.",
                type="error",
                dedup_key=f"index-error:{index_error.cod_historico_indexacao}",
            )

        return created_count


notification_service = NotificationService(NotificationRepository())
