class IndexRepository:
    """
    Repositório responsável por armazenar o índice invertido.
    """

    def __init__(self):
        self.index = {}

    def add_tokens(self, document_id: str, tokens: list):
        """
        Adiciona tokens ao índice.

        :param document_id: id do documento
        :param tokens: lista de termos
        """

        for token in tokens:

            if token not in self.index:
                self.index[token] = []

            self.index[token].append(document_id)

    def search(self, term: str):
        """
        Busca documentos que contém o termo.

        :param term: termo de busca
        :return: lista de documentos
        """

        return self.index.get(term, [])