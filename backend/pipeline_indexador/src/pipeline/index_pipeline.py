from pipeline_indexador.src.stages.preprocess_stage import PreprocessStage
from pipeline_indexador.src.stages.tokenize_stage import TokenizeStage
from pipeline_indexador.src.stages.remove_stopwords_stage import RemoveStopwordsStage
from pipeline_indexador.src.stages.index_build_stage import IndexBuildStage


class IndexPipeline:
    """
    Pipeline responsável por executar as etapas de indexação.
    """

    def __init__(self, index_repository):
        self.stages = [
            PreprocessStage(),
            TokenizeStage(),
            RemoveStopwordsStage(),
            IndexBuildStage(repository=index_repository)
        ]

    def add_stage(self, stage):
        """
        Adiciona uma etapa ao pipeline.

        :param stage: instância de PipelineStage
        """
        self.stages.append(stage)

    def run(self, context: dict) -> dict:
        """
        Executa todas as etapas do pipeline.

        :param context: dados iniciais do documento
        :return: contexto final
        """

        current_context = context

        for stage in self.stages:
            current_context = stage.execute(current_context)

        return current_context