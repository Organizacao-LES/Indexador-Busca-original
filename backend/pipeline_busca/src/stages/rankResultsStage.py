from src.pipeline.pipeline_stage import PipelineStage
from collections import Counter

class RankResultsStage(PipelineStage):

    """
    Etapa responsável por ordenar os documentos
    de acordo com a relevância.
    """
    
    def execute(self, context: dict) -> dict:

        # Recupera a lista de documentos encontrados
        documents = context.get("documents", [])

        # Conta quantas vezes cada documento apareceu
        ranking = Counter(documents)

        # Ordena os documentos pela frequência
        ordered_results = sorted(
            ranking.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Salva os resultados ordenados
        context["results"] = ordered_results

        return context