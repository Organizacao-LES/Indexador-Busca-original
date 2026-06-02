class PipelineStage:
    """
    Classe base para etapas do pipeline de indexação.
    """

    def execute(self, context: dict) -> dict:
        """
        Executa a etapa do pipeline.

        :param context: dados do documento sendo processado
        :return: contexto atualizado
        """
        raise NotImplementedError("execute() deve ser implementado pelas subclasses")