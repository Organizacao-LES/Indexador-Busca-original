# Arquitetura do Backend Completo (`backend`)

## Visao geral

O backend do IFESDOC e uma API FastAPI organizada como monolito modular. Ele
concentra autenticacao, usuarios, ingestao documental, versionamento, OCR,
indexacao, busca, metricas, feedback, notificacoes, bot conversacional e
integracao com PostgreSQL.

Este documento detalha apenas o backend. A visao completa do sistema, incluindo
frontend, infraestrutura e prompt de diagrama, esta em:

- `docs/arquitetura.md`
- `docs/prompt_diagrama_arquitetura_ifesdoc.md`

## Visao macro

```text
FastAPI /api/v1
  -> schemas Pydantic
  -> dependencies de auth/JWT/roles
  -> services de aplicacao
  -> repositories
  -> modelos de dominio SQLAlchemy
  -> PostgreSQL
  -> storage/documents

Fluxos internos relevantes:
  DocumentService -> Adapters/OCR -> IndexService -> Pipeline -> Indice
  SearchService -> QueryAnalyzer -> Strategies -> PostgreSQL/Indice/Embeddings
  BotService -> Intent/Entities -> SearchService -> Formatter
  Notification worker -> NotificationService -> PostgreSQL
```

## Estrutura principal

```text
backend/
  app/
    api/v1/
    adapters/
    bot/
    core/
    domain/
    exceptions/
    pipeline/
    repositories/
    schemas/
    services/
    strategies/
    tests/
    utils/
    workers/
    main.py
  pipeline_indexador/
  pipeline_busca/
  requirements.txt
  Dockerfile
```

## Camada de bootstrap e infraestrutura interna

### `backend/app/main.py`

Responsabilidades:

- cria a instancia FastAPI com titulo `IFESDOC API`;
- registra o roteador versionado em `/api/v1`;
- configura CORS por `BACKEND_CORS_ORIGINS`;
- inicializa tabelas SQLAlchemy no `lifespan`;
- garante complementos de schema para metadados, OCR e Full-Text Search;
- cria administrador inicial quando `INITIAL_ADMIN_PASSWORD` esta configurada;
- registra handlers globais de erro HTTP, validacao e banco indisponivel;
- expoe `GET /` como health check.

### `backend/app/core/`

Responsabilidades:

- `config.py`: configuracoes por ambiente com `pydantic-settings`;
- `database.py`: engine, `SessionLocal`, `Base` e dependencia `get_db`;
- `security.py`: hash de senha, verificacao, JWT e sessoes;
- `dependencies.py`: `get_current_user` e `require_roles`;
- `schema.py`: ajustes incrementais de schema para FTS, OCR e metadados;
- `logging.py`: logger compartilhado.

## Camada HTTP

Local: `backend/app/api/v1/`.

As rotas sao versionadas e agregadas por `router.py`.

| Prefixo | Responsabilidade |
| --- | --- |
| `/auth` | Login, usuario autenticado e logout |
| `/users` | CRUD administrativo de usuarios |
| `/ingestion` | Upload individual, lote e historico de ingestao |
| `/documents` | Detalhes, versoes, download, exportacao, exclusao e reindexacao |
| `/search` | Busca, analise de query, comparacao de estrategias e historico |
| `/index` | Status do indice e reindexacao geral |
| `/ocr` | OCR manual, status e reprocessamento |
| `/metrics` | Indicadores, relatorios e exportacoes |
| `/notifications` | Listagem, leitura e contagem de notificacoes |
| `/feedback` | Feedback de relevancia dos resultados |
| `/bot` | Teste local e webhooks Telegram/WhatsApp |
| `/history` | Historico administrativo |
| `/settings` | Configuracoes da aplicacao |

As rotas devem permanecer finas: recebem dados, aplicam dependencias e chamam
services. A regra de negocio fica na camada `services/`.

## Schemas e contratos

Local: `backend/app/schemas/`.

Os schemas Pydantic definem request/response da API e mantem o contrato separado
das entidades SQLAlchemy. Existem schemas para:

- autenticacao;
- usuarios;
- documentos;
- busca e analise de query;
- indexacao;
- OCR;
- metricas;
- notificacoes;
- feedback;
- historico;
- bot;
- configuracoes.

## Camada de aplicacao

Local: `backend/app/services/`.

### Services principais

- `AuthService`: login, validacao de senha, emissao de token e resposta de
  sessao.
- `UserService`: regras administrativas de usuarios.
- `DocumentService`: upload, validacao, storage, versionamento, metadados,
  download, exportacao, exclusao logica/fisica e integracao com indexacao.
- `IndexService`: indexacao e reindexacao de documentos.
- `InvertedIndexService`: persistencia de campos, termos, postings e estatisticas
  do indice invertido.
- `SearchService`: query analyzer, filtros, escolha de estrategia, ranking,
  snippets, paginacao e historico.
- `QueryAnalyzer`: normalizacao, tokenizacao, termos relevantes, filtros
  implicitos, frases, operadores simples e termos excluidos.
- `SemanticSearchService`: embeddings, busca semantica e reconstrucao vetorial.
- `OCRService`: OCR automatico/manual, registro de status e reindexacao apos OCR.
- `MetricsService`: metricas de acesso, busca, relatorios e calculos.
- `NotificationService`: notificacoes de usuario e alertas administrativos.
- `BotService`: fluxo conversacional, busca via mensagem e resposta formatada.
- `FeedbackService`: feedback de relevancia.
- `SettingsService`: configuracoes consumidas pelo frontend.
- `AdministrativeHistoryService`: auditoria administrativa.

## Dominio

Local: `backend/app/domain/`.

O dominio e mapeado com SQLAlchemy. As entidades representam o modelo relacional
do IFESDOC:

- usuarios e sessoes: `User`, `UserRole`, `UserSession`;
- documentos: `Document`, `DocumentMetadata`, `DocumentHistory`,
  `DocumentCategory`, `InvalidDocument`;
- ingestao e indexacao: `IngestionHistory`, `IngestionStatus`, `IndexHistory`;
- indice: `FieldType`, `DocumentField`, `Term`, `InvertedIndex`;
- busca: `SearchHistory`, `RelevanceFeedback`, `DocumentEmbedding`;
- OCR: `OCRHistory`;
- operacao: `MetricCalculation`, `Notification`, `AdministrativeHistory`;
- bot: `BotConversation`, `BotInteraction`, `BotUserLink`.

## Repositories

Local: `backend/app/repositories/`.

Os repositories encapsulam acesso ao banco e evitam SQL espalhado nos services.

Repositories relevantes:

- `UserRepository`;
- `SessionRepository`;
- `DocumentRepository`;
- `SearchRepository`;
- `PostgresSearchRepository`;
- `EmbeddingRepository`;
- `NotificationRepository`;
- `BotRepository`;
- `AdministrativeHistoryRepository`.

`PostgresSearchRepository` concentra a busca textual nativa com PostgreSQL,
incluindo `websearch_to_tsquery`, `ts_rank_cd`, `ts_headline` e filtros.

## Adapters

Local: `backend/app/adapters/`.

Os adapters isolam bibliotecas externas e formatos de entrada.

| Adapter | Papel |
| --- | --- |
| `DocumentAdapter` | Interface base dos parsers |
| `DocumentAdapterRegistry` | Seleciona adapter por extensao |
| `PdfDocumentAdapter` | Extrai texto de PDF com `pdfplumber` |
| `DocxDocumentAdapter` | Extrai texto de DOCX com `python-docx` |
| `TxtDocumentAdapter` | Extrai texto de TXT |
| `CsvDocumentAdapter` | Extrai texto de CSV |
| `OCRAdapter` | OCR em PDF com Tesseract, `pdf2image` e Pillow |
| `EmbeddingAdapter` | Interface de embedding |
| `MockEmbeddingAdapter` | Embedding deterministico/local para busca semantica |

## Pipeline de indexacao

Local: `backend/app/pipeline/`.

O pipeline integrado ao backend e usado por `IndexService`.

```text
DocumentIngestionPipeline
  -> TextPreprocessStage
  -> TextTokenizeStage
  -> RelationalIndexPersistStage
  -> SemanticEmbeddingPersistStage
```

Responsabilidades das etapas:

- `TextPreprocessStage`: normaliza texto, remove ruido e prepara dados por
  campo;
- `TextTokenizeStage`: valida tokens e monta payload de indexacao;
- `RelationalIndexPersistStage`: grava `tipo_campo`, `campo_documento`,
  `termo` e `indice_invertido`;
- `SemanticEmbeddingPersistStage`: gera e persiste embedding da versao ativa.

Os modulos `backend/pipeline_indexador/` e `backend/pipeline_busca/` continuam no
repositorio como pipelines separados e didaticos para indexacao e busca em
memoria.

## Strategies de busca

Local: `backend/app/strategies/`.

`SearchService` seleciona a estrategia pelo parametro `mode` da busca.

| Modo | Classe | Papel |
| --- | --- | --- |
| `frequency` | `FrequencyRankingStrategy` | Frequencia simples de termos |
| `tfidf` | `TFIDFRankingStrategy` | Frequencia ponderada por raridade |
| `bm25` | `BM25RankingStrategy` | Ranking estatistico para textos |
| `postgres_fts` | `PostgresFTSSearchStrategy` | Busca nativa PostgreSQL FTS |
| `semantic` | `SemanticRankingStrategy` | Similaridade vetorial |
| `hybrid` | `HybridRankingStrategy` | Combina textual e semantico |
| `hybrid_postgres` | `HybridPostgresSearchStrategy` | Combina FTS e ranking secundario |

## Padroes de projeto usados

### Strategy Pattern

Usado na busca. O `SearchService` nao implementa todos os calculos de ranking em
linha; ele delega para strategies especializadas. Isso permite comparar e trocar
algoritmos sem alterar o contrato da API.

Arquivos principais:

- `backend/app/services/search_service.py`;
- `backend/app/strategies/`.

### Pipeline Pattern

Usado na indexacao. O `IndexService` envia um contexto por etapas ordenadas,
onde cada stage faz uma transformacao clara ate o documento ficar pesquisavel.

Arquivos principais:

- `backend/app/services/index_service.py`;
- `backend/app/pipeline/document_ingestion_pipeline.py`;
- `backend/app/pipeline/stages.py`.

### Padroes de apoio

- Repository Pattern em `repositories/`;
- Adapter Pattern em `adapters/` e `bot/`;
- Service Layer em `services/`;
- DTO/Schema em `schemas/`.

## Persistencia e PostgreSQL

O PostgreSQL e responsavel por:

- dados cadastrais;
- documentos e versoes;
- historicos de ingestao, documento, indexacao, busca, OCR e administracao;
- indice invertido relacional;
- feedback de relevancia;
- notificacoes;
- metricas;
- conversas do bot;
- embeddings.

O sistema tambem usa PostgreSQL Full-Text Search:

- coluna `historico_documento.search_vector`;
- trigger para manter o vetor atualizado;
- indice GIN;
- ranking com `ts_rank_cd`;
- highlight com `ts_headline`.

Scripts principais:

- `docker/postgres/init/01_schema.sql`;
- `docker/postgres/init/02_admin.sql`;
- `docker/postgres/init/03_full_text_search.sql`;
- `docker/postgres/init/04_ocr_support.sql`.

## Fluxos principais

### Autenticacao

```text
POST /api/v1/auth/login
  -> AuthService
  -> UserRepository
  -> verify_password
  -> create_access_token
  -> UserSession
  -> TokenResponse
```

### Ingestao

```text
POST /api/v1/ingestion/upload
  -> DocumentService
  -> DocumentAdapterRegistry
  -> parser por extensao
  -> OCRService se texto insuficiente
  -> storage/documents
  -> metadados e versao no PostgreSQL
  -> IndexService
  -> DocumentIngestionPipeline
  -> indice invertido e embedding
```

### Busca

```text
GET /api/v1/search
  -> get_current_user
  -> SearchService
  -> QueryAnalyzer
  -> Strategy por mode
  -> SearchRepository/PostgresSearchRepository/EmbeddingRepository
  -> resposta paginada com score, snippet e metadados
  -> SearchHistory
```

### OCR

```text
POST /api/v1/ocr/document/{document_id}
  -> OCRService
  -> OCRAdapter
  -> Tesseract
  -> atualiza historico_documento
  -> registra historico_ocr
  -> reindexa documento quando aplicavel
```

### Bot

```text
Webhook Telegram/WhatsApp
  -> adapter do canal
  -> BotService
  -> IntentDetector / EntityExtractor
  -> QueryAnalyzer / SearchService
  -> MessageFormatter
  -> resposta ao canal
```

## Worker de notificacoes

Local: `backend/app/workers/notification_worker.py`.

O worker roda em container separado no Docker Compose e periodicamente:

- procura documentos invalidos recentes;
- procura falhas recentes de indexacao;
- cria notificacoes para administradores;
- envia notificacao de disponibilidade do worker com chave de deduplicacao.

## Testes

Locais:

- `backend/app/tests/`;
- `backend/tests/`;
- `backend/pipeline_indexador/src/tests/`.

Coberturas relevantes:

- autenticacao e seguranca;
- usuarios;
- busca e estrategias;
- indexacao e indice invertido;
- ingestao;
- documentos e versionamento;
- OCR;
- notificacoes;
- bot;
- metricas.

## Infraestrutura backend

Arquivos principais:

- `backend/requirements.txt`: dependencias efetivas do backend;
- `backend/Dockerfile`: imagem da API;
- `docker/docker-compose.yml`: API, PostgreSQL, worker, frontend e SonarQube;
- `.env.example`: variaveis de ambiente esperadas.

Configuracoes importantes:

- `DATABASE_URL`;
- `SECRET_KEY`;
- `INITIAL_ADMIN_PASSWORD`;
- `BACKEND_CORS_ORIGINS`;
- `DOCUMENT_UPLOAD_DIR`;
- `DOCUMENT_ALLOWED_EXTENSIONS`;
- variaveis de OCR;
- variaveis de bot Telegram/WhatsApp;
- `NOTIFICATION_WORKER_INTERVAL_SECONDS`.

## Diagnostico arquitetural

O backend atual ja possui mais do que autenticacao: ele concentra o ciclo
principal de documentos, busca, indexacao, OCR, metricas, notificacoes e bot.
A arquitetura segue coerente com separacao em camadas e usa os dois padroes mais
importantes para sua evolucao:

- Strategy, para trocar e comparar rankings de busca;
- Pipeline, para organizar a indexacao documental por etapas.

Os principais pontos de evolucao natural sao:

- mover processamentos pesados para filas dedicadas quando necessario;
- ampliar embeddings reais em substituicao ao adapter mockado;
- consolidar migracoes com Alembic;
- ampliar observabilidade operacional;
- aumentar cobertura de testes de ponta a ponta.
