class IndexRepository:
    """
    Repositório responsável por armazenar o índice invertido.
    O índice invertido é uma estrutura onde cada termo (palavra)
    aponta para uma lista de documentos que contêm esse termo.

    Exemplo de estrutura interna do índice:

    {
        "python": ["doc1", "doc2"],
        "dados": ["doc1"],
        "busca": ["doc1", "doc3"]
    }

    Isso permite recuperar rapidamente os documentos
    que contêm determinado termo de busca.
    """

    def __init__(self):       
        """
        Construtor da classe.

        Inicializa o índice invertido como um dicionário vazio.

        Estrutura:
        termo -> lista de documentos
        """
        self.index = {}

    def add_tokens(self, document_id: str, tokens: list):
        """
        Adiciona tokens (palavras) de um documento ao índice.

        :param document_id: identificador do documento
        :param tokens: lista de palavras extraídas do documento


        Para cada token do documento:
        - verifica se o token já existe no índice
        - se não existir, cria uma nova entrada
        - adiciona o documento à lista de documentos do token
        """
        for token in tokens:

            # Se o token ainda não existe no índice
            if token not in self.index:
                
                 # cria uma nova lista para armazenar documentos
                self.index[token] = []
                
            # adiciona o documento na lista do token
            self.index[token].append(document_id)

    def search(self, term: str):
        """       
        Busca documentos que contêm um termo específico.

        :param term: termo de busca
        :return: lista de documentos que contêm o termo

        Se o termo não existir no índice,
        retorna uma lista vazia.      
        """
        return self.index.get(term, [])


    def search_tokens(self, tokens: list):
        """       
        Busca documentos para vários tokens (palavras).

        :param tokens: lista de termos de busca
        :return: lista de documentos encontrados

        Para cada token:
        - recupera os documentos associados
        - adiciona à lista de resultados

        Esse método é usado pelo pipeline de busca
        para consultas com múltiplas palavras.      
        """

        documents = []

        for token in tokens:
            # busca documentos para o token
            docs = self.index.get(token, [])
            
            # adiciona os documentos encontrados
            documents.extend(docs)

        return documents