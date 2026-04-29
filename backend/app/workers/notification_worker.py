import logging
import time

from sqlalchemy.exc import OperationalError

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.domain.administrative_history import AdministrativeHistory
from app.domain.document import Document
from app.domain.document_category import DocumentCategory
from app.domain.document_field import DocumentField
from app.domain.document_history import DocumentHistory
from app.domain.document_metadata import DocumentMetadata
from app.domain.field_type import FieldType
from app.domain.index_history import IndexHistory
from app.domain.ingestion_history import IngestionHistory
from app.domain.ingestion_status import IngestionStatus
from app.domain.invalid_document import InvalidDocument
from app.domain.notification import Notification
from app.domain.search_history import SearchHistory
from app.domain.term import Term
from app.domain.user import User
from app.services.notification_service import notification_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("ifesdoc.notification_worker")


def run_cycle() -> int:
    db = SessionLocal()
    try:
        created = notification_service.notify_recent_failures(db)
        created += notification_service.notify_admins(
            db,
            title="Notificações ativas",
            message="O serviço de notificações do IFESDOC está em execução.",
            type="success",
            dedup_key="notification-worker:online:v1",
        )
        return created
    finally:
        db.close()


def main() -> None:
    interval = max(10, settings.NOTIFICATION_WORKER_INTERVAL_SECONDS)
    Base.metadata.create_all(bind=engine)
    logger.info("Worker de notificações iniciado. Intervalo: %ss", interval)

    while True:
        try:
            created = run_cycle()
            if created:
                logger.info("%s notificação(ões) criada(s).", created)
        except OperationalError as exc:
            logger.warning("Banco indisponível para notificações: %s", exc)
        except Exception:
            logger.exception("Erro inesperado no worker de notificações.")

        time.sleep(interval)


if __name__ == "__main__":
    main()
