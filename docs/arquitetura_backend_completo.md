# Arquitetura do Backend Completo (`backend`)

## Visão geral

O backend do IFESDOC foi estruturado para suportar duas dimensões complementares:

- uma API REST principal em `backend/app`, desenhada com FastAPI e organização em camadas;
- pipelines especializados de indexação e busca em `backend/pipeline_indexador` e `backend/pipeline_busca`.

Hoje, a estrutura arquitetural está mais avançada do que a implementação efetiva da API. Em termos práticos:

- a pasta `backend/app` define a arquitetura alvo do sistema, mas quase todos os módulos ainda estão vazios;
- as implementações concretas existentes estão concentradas nos pipelines experimentais de indexação e busca;
- `backend/app/main.py` expõe apenas um endpoint raiz simples.

Este documento descreve a arquitetura real do repositório e separa explicitamente:

- o que já está implementado;
- o que já está modelado estruturalmente, mas ainda sem código.

## Visão arquitetural macro

```text
Frontend (interface-web)
  -> chama API REST esperada em /api/v1/*

backend/app
  -> FastAPI
  -> camadas: api, services, repositories, domain, schemas, core, strategies, adapters, pipeline

backend/pipeline_indexador
  -> pipeline independente de indexação textual
  -> pré-processa, tokeniza e constrói índice invertido em memória

backend/pipeline_busca
  -> pipeline independente de busca
  -> normaliza consulta, tokeniza, consulta índice e ranqueia resultados
```

## Organização da pasta `backend/`

- `backend/app/`: núcleo arquitetural da API principal.
- `backend/pipeline_indexador/`: implementação funcional do pipeline de indexação.
- `backend/pipeline_busca/`: implementação funcional do pipeline de busca.
- `backend/tests/`: testes do backend principal.
- `backend/Dockerfile`: reservado para containerização do backend, mas atualmente vazio.

## 1. Núcleo da API principal: `backend/app/`

Essa pasta representa a arquitetura-alvo do backend. Ela foi desenhada para seguir uma separação inspirada em Clean Architecture, Service Layer, Repository Pattern e Strategy Pattern.

### Estrutura e função de cada diretório/pacote

#### `backend/app/main.py`

É o ponto de entrada atual da API principal.

Responsabilidades atuais:

- instancia o `FastAPI`;
- define metadados básicos da aplicação;
- expõe `GET /` com mensagem de status.

Estado atual:

- implementado, porém minimalista;
- ainda não integra `router.py`, middlewares, dependências, autenticação ou banco.

#### `backend/app/api/`

Camada HTTP da aplicação. Deve receber requisições, validar entradas e delegar para serviços.

##### `backend/app/api/v1/`

- pacote de versionamento da API REST.
- deveria concentrar os routers por domínio.

Arquivos:

- `router.py`: agregador principal de rotas versionadas. Está vazio.
- `search_routes.py`: previsto para endpoints de busca. Está vazio.
- `document_routes.py`: previsto para endpoints de documentos. Está vazio.
- `user_routes.py`: previsto para endpoints de usuários. Está vazio.
- `health_routes.py`: previsto para health checks e readiness. Está vazio.
- `__init__.py`: marcador de pacote.

Função arquitetural do pacote:

- isolar a camada web;
- manter a lógica HTTP separada da regra de negócio;
- padronizar contratos da API versão `v1`.

#### `backend/app/core/`

Pacote reservado para infraestrutura transversal.

Arquivos:

- `config.py`: destinado a configurações e leitura de ambiente. Está vazio.
- `database.py`: destinado à conexão SQLAlchemy, sessão e engine. Está vazio.
- `logging.py`: destinado a logging estruturado. Está vazio.
- `security.py`: destinado a autenticação, hash e tokens. Está vazio.
- `__init__.py`: marcador de pacote.

Função arquitetural esperada:

- bootstrap técnico da aplicação;
- recursos compartilhados de configuração, banco, segurança e observabilidade.

#### `backend/app/domain/`

Pacote do domínio puro do sistema.

Arquivos:

- `document.py`: entidade de documento. Está vazio.
- `user.py`: entidade de usuário. Está vazio.
- `term.py`: entidade de termo/indexação. Está vazio.
- `index.py`: entidade relacionada ao índice. Está vazio.
- `search.py`: objetos de busca. Está vazio.
- `__init__.py`: marcador de pacote.

Função arquitetural esperada:

- representar as entidades centrais do negócio;
- abrigar regras puras, sem dependência de framework.

#### `backend/app/schemas/`

Pacote de contratos de entrada e saída, provavelmente orientado a Pydantic.

Arquivos:

- `document_schema.py`: contratos de documentos. Está vazio.
- `user_schema.py`: contratos de usuários. Está vazio.
- `search_schema.py`: contratos de busca. Está vazio.
- `feedback_schema.py`: contratos auxiliares de resposta/feedback. Está vazio.
- `__init__.py`: marcador de pacote.

Função arquitetural esperada:

- validar payloads HTTP;
- serializar respostas;
- separar modelos externos dos modelos internos de domínio.

#### `backend/app/services/`

Camada de casos de uso e orquestração.

Arquivos:

- `search_service.py`: serviço de busca da API principal. Está vazio.
- `ingestion_service.py`: serviço de ingestão. Está vazio.
- `document_service.py`: serviço de documentos. Está vazio.
- `user_service.py`: serviço de usuários. Está vazio.
- `index_service.py`: serviço de indexação e status. Está vazio.
- `__init__.py`: marcador de pacote.

Função arquitetural esperada:

- coordenar regras de negócio;
- chamar repositórios, estratégias e adapters;
- manter controladores HTTP finos.

#### `backend/app/repositories/`

Camada de persistência abstrata.

Arquivos:

- `document_repository.py`: acesso a documentos. Está vazio.
- `user_repository.py`: acesso a usuários. Está vazio.
- `term_repository.py`: acesso a termos. Está vazio.
- `index_repository.py`: acesso ao índice. Está vazio.
- `search_repository.py`: consultas especializadas de busca. Está vazio.
- `__init__.py`: marcador de pacote.

Função arquitetural esperada:

- encapsular SQL e persistência;
- evitar dependência direta do banco nas camadas superiores.

#### `backend/app/strategies/`

Pacote de algoritmos intercambiáveis.

Arquivos:

- `ranking_strategy.py`: interface base de ranking. Está vazio.
- `bm25_strategy.py`: estratégia BM25. Está vazio.
- `tfidf_strategy.py`: estratégia TF-IDF. Está vazio.
- `__init__.py`: marcador de pacote.

Função arquitetural esperada:

- permitir troca de estratégia de relevância sem alterar serviços;
- sustentar evolução do motor de busca.

#### `backend/app/adapters/`

Pacote de integração com fontes externas e formatos de documento.

Arquivos:

- `pdf_parser.py`: parser de PDF. Está vazio.
- `file_storage.py`: abstração de armazenamento de arquivos. Está vazio.
- `tokenizer.py`: adaptação de tokenização. Está vazio.
- `__init__.py`: marcador de pacote.

Função arquitetural esperada:

- desacoplar parsing, storage e ferramentas externas da lógica de negócio.

#### `backend/app/pipeline/`

Pacote reservado para pipelines integrados à API principal.

Arquivos:

- `ingestion_pipeline.py`: pipeline de ingestão. Está vazio.
- `indexing_pipeline.py`: pipeline de indexação. Está vazio.
- `search_pipeline.py`: pipeline de busca. Está vazio.
- `__init__.py`: marcador de pacote.

Função arquitetural esperada:

- orquestrar fluxos multiestágio dentro da aplicação principal.

#### `backend/app/exceptions/`

- pacote para exceções customizadas;
- atualmente contém apenas `__init__.py` vazio.

#### `backend/app/utils/`

Pacote de utilidades técnicas.

Arquivos:

- `pagination.py`: utilitário esperado para paginação. Está vazio.
- `text_processing.py`: utilitário esperado para normalização textual. Está vazio.
- `time_utils.py`: arquivo praticamente vazio.
- `__init__.py`: marcador de pacote.

Função arquitetural esperada:

- concentrar helpers reutilizáveis que não pertencem ao domínio puro.

### Diagnóstico do estado de `backend/app`

Arquiteturalmente, `backend/app` está bem desenhado como destino final do sistema. Porém, em implementação:

- apenas `main.py` possui código funcional;
- quase todos os pacotes existem como esqueleto;
- a API REST consumida pelo frontend ainda não foi conectada de fato.

## 2. Pipeline funcional de indexação: `backend/pipeline_indexador/`

Esse é o módulo backend mais implementado no repositório. Ele modela o fluxo de indexação textual como pipeline sequencial em memória.

## Função da pasta

- demonstrar o processo de indexação de um documento;
- servir como prova de conceito para o motor de indexação;
- aplicar o padrão Pipeline/Chain of Responsibility.

## Estrutura e função de cada diretório

### `backend/pipeline_indexador/app.py`

Script de execução manual do indexador.

Responsabilidades:

- instancia `IndexerService`;
- envia um documento de exemplo para indexação;
- imprime confirmação no terminal.

### `backend/pipeline_indexador/src/`

Código-fonte do pipeline de indexação.

#### `backend/pipeline_indexador/src/indexer/`

##### `indexer_service.py`

Serviço principal do módulo de indexação.

Responsabilidades:

- instanciar `IndexRepository`;
- montar `IndexPipeline`;
- registrar as etapas `PreprocessStage`, `TokenizeStage` e `IndexBuildStage`;
- expor `index_document(document_id, text)`.

É a fachada principal do pipeline.

#### `backend/pipeline_indexador/src/pipeline/`

Infraestrutura genérica do pipeline.

##### `pipeline_stage.py`

- classe base abstrata das etapas;
- define o contrato `execute(context: dict) -> dict`.

##### `index_pipeline.py`

- pipeline sequencial;
- mantém lista ordenada de etapas;
- executa cada estágio sobre um `context` compartilhado.

Função arquitetural do pacote:

- padronizar execução em etapas;
- facilitar extensão por novos estágios.

#### `backend/pipeline_indexador/src/stages/`

Etapas concretas do pipeline.

##### `preprocess_stage.py`

- normaliza texto de entrada;
- converte para minúsculas;
- remove pontuação com regex;
- grava `processed_text` no contexto.

##### `tokenize_stage.py`

- divide o texto normalizado por espaços;
- grava `tokens` no contexto.

##### `index_build_stage.py`

- lê `document_id` e `tokens`;
- envia os tokens ao repositório;
- atualiza o índice invertido em memória.

Função arquitetural do pacote:

- separar cada transformação em unidades independentes e composáveis.

#### `backend/pipeline_indexador/src/storage/`

##### `index_repository.py`

Repositório em memória do índice invertido.

Responsabilidades:

- manter `self.index` como dicionário;
- criar entradas por token;
- associar cada token a uma lista de documentos;
- oferecer `search(term)` para recuperação simples.

Observação importante:

- a persistência atual é totalmente volátil;
- não há banco, arquivo ou sincronização com `backend/app/repositories`.

#### `backend/pipeline_indexador/src/tests/`

- reservado para testes do pipeline;
- `pipeline_test.py` existe, mas está vazio.

## Fluxo interno do indexador

```text
IndexerService.index_document()
  -> IndexPipeline.run()
    -> PreprocessStage.execute()
    -> TokenizeStage.execute()
    -> IndexBuildStage.execute()
      -> IndexRepository.add_tokens()
```

## 3. Pipeline funcional de busca: `backend/pipeline_busca/`

Esse módulo implementa a busca textual como pipeline independente, também em memória.

## Função da pasta

- demonstrar como uma consulta é processada;
- aplicar tokenização e normalização à query;
- recuperar documentos do índice;
- ranquear resultados por frequência.

## Estrutura e função de cada diretório

### `backend/pipeline_busca/src/search_app.py`

Script manual de demonstração do fluxo de busca.

Responsabilidades:

- instancia `SearchService`;
- executa uma consulta fixa;
- imprime o resultado no terminal.

### `backend/pipeline_busca/src/search/`

##### `search_service.py`

Serviço principal do módulo de busca.

Responsabilidades:

- instanciar `IndexRepository`;
- montar `SearchPipeline`;
- registrar as etapas `QueryPreprocessStage`, `QueryTokenizeStage`, `SearchIndexStage` e `RankResultsStage`;
- expor `search(query)`.

Observação arquitetural:

- esse serviço cria seu próprio repositório em memória;
- ele não compartilha estado com `pipeline_indexador`, a menos que isso seja integrado manualmente no futuro.

### `backend/pipeline_busca/src/pipeline/`

Infraestrutura genérica do pipeline de busca.

##### `pipeline_stage.py`

- classe base de estágios do pipeline;
- impõe a implementação de `execute`.

##### `search_pipeline.py`

- controla a ordem das etapas de busca;
- executa a transformação progressiva do contexto até gerar resultados.

### `backend/pipeline_busca/src/stages/`

Etapas do pipeline de consulta.

##### `queryPreprocessStage.py`

- normaliza a consulta;
- remove pontuação e converte para minúsculas;
- grava `processed_query`.

##### `queryTokenizeStage.py`

- divide `processed_query` em palavras;
- grava `tokens`.

##### `searchIndexStage.py`

- recebe tokens;
- consulta o índice invertido via repositório;
- grava `documents` encontrados.

##### `rankResultsStage.py`

- usa `collections.Counter`;
- conta frequência de ocorrência dos documentos;
- ordena por maior frequência;
- grava `results`.

### `backend/pipeline_busca/src/storage/`

##### `index_repository.py`

Repositório em memória do índice invertido para o módulo de busca.

Responsabilidades:

- manter estrutura `termo -> [documentos]`;
- permitir `add_tokens(document_id, tokens)`;
- permitir `search(term)`;
- permitir `search_tokens(tokens)` para buscas multi-termo.

Observação importante:

- esse repositório duplica a ideia do repositório do indexador;
- ainda não existe uma infraestrutura única compartilhada entre indexação e busca;
- por isso, a arquitetura atual é demonstrativa, não um backend consolidado fim a fim.

## Fluxo interno da busca

```text
SearchService.search()
  -> SearchPipeline.run()
    -> QueryPreprocessStage.execute()
    -> QueryTokenizeStage.execute()
    -> SearchIndexStage.execute()
      -> IndexRepository.search_tokens()
    -> RankResultsStage.execute()
```

## 4. Testes do backend principal

### `backend/tests/`

- `test_main.py`: testa a função `root()` de `backend/app/main.py`.
- `__init__.py`: marcador de pacote.

Estado atual:

- há apenas um teste básico de sanidade;
- cobertura ainda não alcança serviços, pipelines, repositórios ou API REST versionada.

## 5. Relação com a infraestrutura do projeto

Embora esteja fora de `backend/`, alguns arquivos da raiz impactam a arquitetura backend.

### `requirements.txt`

Define as dependências pretendidas do backend:

- `fastapi`, `uvicorn`, `python-multipart`, `python-dotenv`;
- `sqlalchemy`, `psycopg2-binary`, `alembic`;
- `pydantic`;
- `python-jose`, `passlib`, `bcrypt`;
- `pdfplumber`, `unidecode`;
- `pytest`, `pytest-cov`.

Leitura arquitetural:

- o backend foi planejado para autenticação por token, persistência relacional, parsing de PDF e testes;
- porém boa parte disso ainda não aparece no código implementado.

### `docker/docker-compose.yml`

Hoje a infraestrutura containerizada disponível está focada em apoio ao backend:

- `postgres`: banco principal do projeto (`ifesdoc`);
- `sonarqube_db`: banco do SonarQube;
- `sonarqube`: análise de qualidade.

Papel na arquitetura:

- fornecer PostgreSQL para a futura camada de persistência do backend;
- suportar análise estática e governança de qualidade.

## Padrões arquiteturais presentes

Mesmo com implementação parcial, o repositório já deixa claros os padrões desejados:

- `Service Layer`: `app/services/`.
- `Repository Pattern`: `app/repositories/` e repositórios dos pipelines.
- `Strategy Pattern`: `app/strategies/`.
- `Adapter Pattern`: `app/adapters/`.
- `Pipeline / Chain of Responsibility`: `pipeline_indexador` e `pipeline_busca`.
- `Layered Architecture`: separação entre API, domínio, serviços, persistência e infraestrutura.

## Diagnóstico final da arquitetura backend

### O que já está implementado

- API FastAPI mínima com endpoint raiz.
- pipeline funcional de indexação em memória.
- pipeline funcional de busca em memória.
- teste simples de sanidade.
- infraestrutura Docker com PostgreSQL e SonarQube.

### O que já está modelado, mas ainda vazio

- camada HTTP versionada em `app/api/v1`;
- domínio em `app/domain`;
- contratos Pydantic em `app/schemas`;
- serviços de negócio em `app/services`;
- persistência em `app/repositories`;
- estratégias de ranking em `app/strategies`;
- infraestrutura transversal em `app/core`;
- adapters de parsing e storage em `app/adapters`.

### Consequência arquitetural prática

O backend completo do repositório ainda está em fase de consolidação. A arquitetura alvo está bem definida, mas a execução real hoje está fragmentada entre:

- uma API principal ainda esquelética;
- pipelines independentes usados como prova de conceito.

Para o sistema funcionar ponta a ponta com o frontend atual, o próximo passo natural seria integrar os pipelines funcionais à camada `backend/app`, preenchendo `services`, `repositories`, `schemas`, `api/v1` e `core`.
