class PipelineStage:
    """
    Classe base para etapas do pipeline de busca.
    """

    def execute(self, context: dict) -> dict:
        """
        Método que executa a lógica da etapa.
        

        :param context: dados do documento sendo processado
        :return: contexto atualizado
        """
        raise NotImplementedError("execute() deve ser implementado pelas subclasses")