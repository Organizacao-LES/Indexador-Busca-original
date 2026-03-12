class IndexPipeline:
    """
    Pipeline responsável por executar as etapas de indexação.
    """

    def __init__(self):
        self.stages = []

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