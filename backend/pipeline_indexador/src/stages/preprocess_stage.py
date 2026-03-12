import re
from src.pipeline.pipeline_stage import PipelineStage


class PreprocessStage(PipelineStage):
    """
    Etapa de pré-processamento do texto.
    """

    def execute(self, context: dict) -> dict:
        """
        Normaliza o texto.

        :param context: contexto do documento
        :return: contexto atualizado
        """

        text = context.get("text", "")

        normalized = re.sub(r"[^\w\s]", "", text.lower())

        context["processed_text"] = normalized

        return context