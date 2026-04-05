from ..pipeline.pipeline_stage import PipelineStage


class RemoveStopwordsStage(PipelineStage):
    """
    Etapa responsável por remover stopwords do texto tokenizado.
    """

    def __init__(self, stopwords: set = None):
        """
        Inicializa a etapa de remoção de stopwords.

        :param stopwords: Um conjunto de stopwords a serem removidas.
                          Se nenhum conjunto for fornecido, um conjunto padrão de português será usado.
        """
        if stopwords is None:
            self.stopwords = {
                "a", "e", "i", "o", "u", "as", "os", "ao", "aos", "de", "da", "do", "das", "dos",
                "em", "no", "na", "nos", "nas", "com", "por", "para", "que", "e", "ou", "mas",
                "um", "uma", "uns", "umas", "o", "a", "os", "as", "é", "não", "se", "para",
                "como", "porém", "mas", "mais", "menos", "este", "esta", "isto", "esse", "essa",
                "isso", "aquele", "aquela", "aquilo", "meu", "minha", "meus", "minhas", "teu",
                "tua", "teus", "tuas", "seu", "sua", "seus", "suas", "nosso", "nossa", "nossos",
                "nossas", "vosso", "vossa", "vossos", "vossas", "qual", "quem", "cujo", "cuja",
                "cujos", "cujas", "onde", "quando", "como", "porque", "porquê", "pelo", "pela",
                "pelos", "pelas", "sem", "sob", "sobre", "entre", "até", "após", "desde", "ante",
                "contra", "durante", "mediante", "segundo", "salvo", "exceto", "comigo", "contigo",
                "consigo", "conosco", "convosco", "nós", "vós", "eles", "elas", "mim", "ti", "si",
                "ele", "ela", "você", "vocês", "lhes", "me", "te", "lhe", "nos", "vos", "quem",
                "já", "ainda", "muito", "pouco", "mais", "menos", "tão", "tanto", "quase", "apenas",
                "somente", "só", "certo", "errado", "talvez", "provavelmente", "sim", "não", "agora",
                "depois", "ontem", "hoje", "amanhã", "sempre", "nunca", "jamais", "aqui", "ali",
                "lá", "cá", "longe", "perto", "dentro", "fora", "acima", "abaixo", "adiante",
                "atrás", "através", "debaixo", "defronte", "defronte", "enfim", "então", "logo",
                "outrora", "pouco", "primeiro", "ser", "estar", "ir", "haver", "ter", "fazer",
                "dizer", "poder", "ver", "dar", "saber", "querer", "ficar", "dever", "vir",
                "algum", "nenhum", "todo", "muito", "pouco", "vários", "diversos", "certo",
                "cada", "outro", "mesmo", "próprio", "cujo", "alguns", "algumas", "nenhuns",
                "nenhumas", "todos", "todas", "muitos", "muitas", "várias", "diversas", "certos",
                "certas", "outros", "outras", "mesmos", "mesmas", "próprios", "próprias"
            }
        else:
            self.stopwords = stopwords

    def execute(self, context: dict) -> dict:
        """
        Remove stopwords de uma lista de tokens.

        :param context: contexto do documento com a lista de tokens
        :return: contexto atualizado com os tokens sem stopwords
        """
        tokens = context.get("tokens", [])
        filtered_tokens = [token for token in tokens if token not in self.stopwords]
        context["tokens"] = filtered_tokens
        return context
