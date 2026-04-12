from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.domain.document import Document
from app.domain.document_category import DocumentCategory
from app.domain.document_field import DocumentField
from app.domain.document_history import DocumentHistory
from app.domain.field_type import FieldType
from app.domain.index_history import IndexHistory
from app.domain.ingestion_history import IngestionHistory
from app.domain.ingestion_status import IngestionStatus
from app.domain.inverted_index import InvertedIndex
from app.domain.term import Term
from app.domain.user import User
from app.domain.user_role import UserRole
from app.services.index_service import index_service


def test_index_status_snapshot_reports_metrics_and_consistency():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = session_local()

    user = User(
        nome="Administrador",
        login="admin",
        email="admin@ifes.edu.br",
        senha_hash="hash",
        perfil=UserRole.ADMIN.value,
        ativo=True,
    )
    category = DocumentCategory(nome_categoria="administrativo")
    status = IngestionStatus(estado_ingestao="concluido")
    field_type = FieldType(tipo_campo="conteudo")
    db.add_all([user, category, status, field_type])
    db.flush()

    document = Document(
        cod_categoria=category.cod_categoria,
        titulo="Portaria",
        tipo="TXT",
        ativo=True,
        cod_usuario_criador=user.cod_usuario,
    )
    db.add(document)
    db.flush()

    history = DocumentHistory(
        cod_documento=document.cod_documento,
        cod_usuario=user.cod_usuario,
        numero_versao=1,
        caminho_arquivo="/tmp/portaria.txt",
        texto_extraido="ifes documento portaria",
        texto_processado="ifes documento portaria",
        versao_ativa=True,
    )
    db.add(history)
    db.flush()

    field = DocumentField(
        cod_historico_documento=history.cod_historico_documento,
        cod_tipo_campo=field_type.cod_tipo_campo,
        conteudo="ifes documento portaria",
    )
    db.add(field)
    db.flush()

    term = Term(texto_termo="ifes", df=1, idf=1000)
    db.add(term)
    db.flush()

    posting = InvertedIndex(
        cod_termo=term.cod_termo,
        cod_campo_documento=field.cod_campo_documento,
        tf=1,
        posicao_inicial=0,
    )
    index_history = IndexHistory(
        cod_historico_documento=history.cod_historico_documento,
        tempo_indexacao_ms=15,
        mensagem_erro=None,
    )
    ingestion_history = IngestionHistory(
        cod_usuario=user.cod_usuario,
        cod_documento=document.cod_documento,
        cod_status_ingestao=status.cod_status_ingestao,
        tipo_ingestao="manual",
        mensagem_erro=None,
        tempo_processamento_ms=30,
    )
    db.add_all([posting, index_history, ingestion_history])
    db.commit()

    snapshot = index_service.get_status_snapshot(db)

    assert snapshot["indexedDocuments"] == 1
    assert snapshot["integrityOk"] is True
    assert snapshot["inconsistencyCount"] == 0
    assert snapshot["consistency"]["documentsWithoutIndex"] == 0
    assert snapshot["metrics"]["activeDocuments"] == 1
    assert snapshot["metrics"]["totalTerms"] == 1
    assert snapshot["metrics"]["totalPostings"] == 1
    assert snapshot["logs"]

    db.close()
    Base.metadata.drop_all(bind=engine)
