class SearchPipeline:
    """  
    Pipeline responsável por executar todas as etapas
    necessárias para realizar uma busca.
    """

    def __init__(self):
        
        # Lista de etapas que compõem o pipeline
        self.stages = []

    def add_stage(self, stage):
        """
        Adiciona uma etapa ao pipeline.        

        :param stage: instância de uma classe que herda de PipelineStage
        """
        self.stages.append(stage)

    def run(self, context: dict) -> dict:
        """
        Executa todas as etapas do pipeline de busca.

        :param context: dados iniciais da busca
        :return: contexto final com os resultados
        """

        # Contexto atual que será transformado pelas etapas
        current_context = context

        # Executa cada etapa em sequência
        for stage in self.stages:
            current_context = stage.execute(current_context)

        # Retorna o contexto final após todas as etapas
        return current_context