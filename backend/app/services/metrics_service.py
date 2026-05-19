from __future__ import annotations

from collections import Counter
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.repositories.metrics_repository import MetricsRepository
from app.services.index_service import index_service
from app.utils.text_processing import preprocess_for_indexing


class MetricsService:
    
    # Injeta o repository seguindo o padrão do projeto
    def __init__(self, metrics_repository: MetricsRepository):
        self.metrics_repository = metrics_repository

    
    # Método principal responsável por montar o snapshot completo
    # de métricas e indicadores de desempenho da busca
    def snapshot(self, db: Session) -> dict:
        
        # Obtém métricas do serviço de indexação
        index_snapshot = index_service.get_status_snapshot(db)
        
        # Total de consultas realizadas
        total_queries = self.metrics_repository.get_total_queries(db)
        
        
        # Tempo médio de resposta das buscas
        average_search_time = (
            self.metrics_repository.get_average_search_time(db)
        )
        
        
        # Média de resultados retornados por consulta
        average_results = (
            self.metrics_repository.get_average_results(db)
        )
        
        
        
         # Quantidade de buscas sem resultado
        queries_without_results = (
            self.metrics_repository.get_queries_without_results(db)
        )
        
       
        
        
        # Taxa percentual de buscas sem resultado
        zero_results_rate = (
            (queries_without_results / total_queries) * 100
            if total_queries
            else 0
        )


        # Data atual
        today = date.today()
        
         # Quantidade de consultas realizadas hoje
        queries_today = self.metrics_repository.get_queries_today(
            db,
            today,
        )
        


        # Histórico de consultas dos últimos 7 dias
        queries_by_day = []
        for days_ago in range(6, -1, -1):
            current_day = today - timedelta(days=days_ago)
            
            
            count = self.metrics_repository.get_queries_count_by_day(
                db,
                current_day,
            )
            
            queries_by_day.append(
                {
                    "day": current_day.strftime("%d/%m"),
                    "consultas": count,
                }
            )


        # Contador de frequência de termos buscados
        term_counter: Counter[str] = Counter()
        # Recupera todas as consultas realizadas
        recent_queries = self.metrics_repository.get_all_queries(db)

        
        # Processa os tokens das consultas  
        for row in recent_queries:
            
            processed = preprocess_for_indexing( 
                row.consulta_texto or ""
            )
            
            for token in processed["tokens"]:
                term_counter[token] += 1


        # Top 5 termos mais pesquisados
        top_terms = [
            {"name": term, "value": count}
            for term, count in term_counter.most_common(5)
        ]

        # Quantidade de documentos agrupados por categoria
        documents_by_category_rows = (
            self.metrics_repository.get_documents_by_category(db)
        )
               
        
        documents_by_category = [
            {"name": row[0], "value": row[1]}
            for row in documents_by_category_rows
        ]
       
        
        # Distribuição das consultas
        query_outcome_distribution = [
            {
                "name": "Com resultados",
                "value": max(total_queries - queries_without_results, 0),
            },
            {
                "name": "Sem resultados",
                "value": queries_without_results,
            },
        ]


        # Snapshot consolidado
        return {
            "overview": {
                "totalQueries": total_queries,
                "averageSearchTime": self._format_duration(average_search_time),
                "indexedDocuments": index_snapshot["indexedDocuments"],
                "successRate": index_snapshot["successRate"],
                "averageResults": f"{float(average_results or 0):.1f}",
                "queriesToday": queries_today,
                "queriesWithoutResults": queries_without_results,
                "zeroResultsRate": f"{zero_results_rate:.1f}%",
            },
            "queriesByDay": queries_by_day,
            "topTerms": top_terms,
            "documentsByCategory": documents_by_category,
            "queryOutcomeDistribution": query_outcome_distribution,
        }


    # Formata tempo de duração para ms ou segundos
    def _format_duration(self, duration_ms: float | None) -> str:
        if duration_ms is None:
            return "0 ms"
        duration_ms = float(duration_ms)
        if duration_ms >= 1000:
            return f"{duration_ms / 1000:.2f}s"
        return f"{duration_ms:.0f} ms"


metrics_service = MetricsService(
    MetricsRepository()
)
