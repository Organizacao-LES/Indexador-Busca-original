from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.main  # noqa: F401
from app.core.database import Base
from app.domain.user import User
from app.domain.user_role import UserRole
from app.services.notification_service import notification_service


def make_session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)()


def test_notification_service_lists_and_marks_user_notifications():
    db = make_session()
    try:
        user = User(
            nome="Usuário Teste",
            login="usuario.teste",
            email="usuario.teste@ifes.edu.br",
            senha_hash="hash",
            perfil=UserRole.USER.value,
            ativo=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        notification = notification_service.create_for_user(
            db,
            user_id=user.cod_usuario,
            title="Mensagem do sistema",
            message="O IFESDOC enviou uma nova mensagem.",
            type="info",
        )

        assert notification is not None
        assert notification_service.unread_count(db, user) == 1

        listed = notification_service.list_for_user(db, user)
        assert listed[0]["title"] == "Mensagem do sistema"
        assert listed[0]["read"] is False

        read = notification_service.mark_read(db, user, notification.cod_notificacao)
        assert read["read"] is True
        assert notification_service.unread_count(db, user) == 0
    finally:
        db.close()
