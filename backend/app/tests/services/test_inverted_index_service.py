from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.domain.document import Document
from app.domain.document_category import DocumentCategory
from app.domain.document_field import DocumentField
from app.domain.document_history import DocumentHistory
from app.domain.inverted_index import InvertedIndex
from app.domain.term import Term
from app.domain.user import User
from app.domain.user_role import UserRole
from app.services.inverted_index_service import inverted_index_service
from app.utils.text_processing import preprocess_for_indexing


def make_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return engine, session_local()


def create_document(db, *, user_id: int, category_id: int, title: str, text: str) -> DocumentHistory:
    document = Document(
        cod_categoria=category_id,
        titulo=title,
        tipo="TXT",
        ativo=True,
        cod_usuario_criador=user_id,
    )
    db.add(document)
    db.flush()

    history = DocumentHistory(
        cod_documento=document.cod_documento,
        cod_usuario=user_id,
        numero_versao=1,
        caminho_arquivo=f"/tmp/{title}.txt",
        texto_extraido=text,
        texto_processado=text,
        versao_ativa=True,
    )
    db.add(history)
    db.flush()
    return history


def index_text(db, history: DocumentHistory, text: str):
    payload = preprocess_for_indexing(text)
    return inverted_index_service.persist_document_terms(
        db,
        history=history,
        processed_text=payload["processed_text"],
        positions_by_term=payload["positions_by_term"],
    )


def test_inverted_index_maps_terms_to_multiple_documents_and_updates_entries():
    engine, db = make_session()

    user = User(
        nome="Administrador",
        login="admin",
        email="admin@ifes.edu.br",
        senha_hash="hash",
        perfil=UserRole.ADMIN.value,
        ativo=True,
    )
    category = DocumentCategory(nome_categoria="administrativo")
    db.add_all([user, category])
    db.flush()

    history_one = create_document(
        db,
        user_id=user.cod_usuario,
        category_id=category.cod_categoria,
        title="Portaria",
        text="ifes pesquisa pesquisa",
    )
    history_two = create_document(
        db,
        user_id=user.cod_usuario,
        category_id=category.cod_categoria,
        title="Edital",
        text="ifes edital",
    )

    result_one = index_text(db, history_one, "ifes pesquisa pesquisa")
    result_two = index_text(db, history_two, "ifes edital")
    db.commit()

    assert result_one == {"term_count": 2, "token_count": 3}
    assert result_two == {"term_count": 2, "token_count": 2}
    assert inverted_index_service.find_document_ids_by_terms(db, ["ifes"]) == [
        history_one.cod_documento,
        history_two.cod_documento,
    ]

    ifes_term = db.query(Term).filter(Term.texto_termo == "ifes").one()
    pesquisa_term = db.query(Term).filter(Term.texto_termo == "pesquisa").one()
    pesquisa_posting = (
        db.query(InvertedIndex)
        .join(DocumentField, DocumentField.cod_campo_documento == InvertedIndex.cod_campo_documento)
        .filter(DocumentField.cod_historico_documento == history_one.cod_historico_documento)
        .filter(InvertedIndex.cod_termo == pesquisa_term.cod_termo)
        .one()
    )

    assert int(ifes_term.df) == 2
    assert pesquisa_posting.tf == 2
    assert pesquisa_posting.posicao_inicial == 1

    index_text(db, history_one, "edital atualizado")
    db.commit()

    db.refresh(ifes_term)
    db.refresh(pesquisa_term)
    assert int(ifes_term.df) == 1
    assert int(pesquisa_term.df) == 0
    assert inverted_index_service.find_document_ids_by_terms(db, ["pesquisa"]) == []
    assert inverted_index_service.find_document_ids_by_terms(db, ["edital"]) == [
        history_one.cod_documento,
        history_two.cod_documento,
    ]

    db.close()
    Base.metadata.drop_all(bind=engine)
