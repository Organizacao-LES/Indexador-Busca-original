# app/repositories/metrics_repository.py

from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.document import Document
from app.domain.document_category import DocumentCategory
from app.domain.search_history import SearchHistory


class MetricsRepository:
    
    # Retorna o total de consultas realizadas
    @staticmethod
    def get_total_queries(db: Session) -> int:

        return (
            db.query(
                func.count(SearchHistory.cod_historico_busca)
            ).scalar()
            or 0
        )
        
    # Retorna o tempo médio de resposta das consultas
    @staticmethod
    def get_average_search_time(db: Session):

        return (
            db.query(
                func.avg(SearchHistory.tempo_resposta_ms)
            ).scalar()
        )
    
    
    # Retorna a média de resultados encontrados por consulta
    @staticmethod
    def get_average_results(db: Session):

        return (
            db.query(
                func.avg(SearchHistory.quantidade_resultados)
            ).scalar()
        )
        
        
    # Retorna a quantidade de consultas sem resultado
    @staticmethod
    def get_queries_without_results(db: Session) -> int:

        return (
            db.query(
                func.count(SearchHistory.cod_historico_busca)
            )
            .filter(
                SearchHistory.quantidade_resultados <= 0
            )
            .scalar()
            or 0
        )
        
        
    # Retorna a quantidade de consultas realizadas em uma data específica
    @staticmethod
    def get_queries_count_by_day(
        db: Session,
        target_date: date,
    ) -> int:

        return (
            db.query(
                func.count(SearchHistory.cod_historico_busca)
            )
            .filter(
                func.date(SearchHistory.criado_em)
                == target_date.isoformat()
            )
            .scalar()
            or 0
        )
        
    
    # Retorna a quantidade de consultas realizadas hoje
    @classmethod
    def get_queries_today(
        cls,
        db: Session,
        today: date,
    ) -> int:

        return cls.get_queries_count_by_day(
            db,
            today,
        )
        
        
    # Retorna todas as consultas realizadas
    # Utilizado para calcular termos mais buscados
    @staticmethod
    def get_all_queries(db: Session):

        return (
            db.query(
                SearchHistory.consulta_texto
            ).all()
        )
        
        
    # Retorna documentos agrupados por categoria
    @staticmethod
    def get_documents_by_category(db: Session):

        return (
            db.query(
                DocumentCategory.nome_categoria,
                func.count(Document.cod_documento),
            )
            .join(
                Document,
                Document.cod_categoria
                == DocumentCategory.cod_categoria,
            )
            .filter(
                Document.ativo.is_(True)
            )
            .group_by(
                DocumentCategory.nome_categoria
            )
            .order_by(
                func.count(Document.cod_documento).desc()
            )
            .all()
        )