# Prompt para Criacao do Diagrama de Arquitetura do IFESDOC

Use este prompt em uma ferramenta de geracao de imagem, ferramenta de desenho
assistida por IA, Figma AI, Whimsical, Miro AI, Excalidraw AI, Mermaid visual ou
em um designer humano. O objetivo e gerar um diagrama limpo, explicavel e nao
poluido.

## Prompt principal

```text
Crie um diagrama de arquitetura de software profissional, em portugues, para o
sistema IFESDOC, uma plataforma web de ingestao, indexacao, busca e auditoria de
documentos.

Formato:
- Layout horizontal 16:9.
- Estilo limpo, academico/profissional, com blocos agrupados por camadas.
- Usar fundo claro.
- Usar poucas cores: verde/teal para frontend, azul para API/backend, roxo para
  busca/indexacao, laranja para OCR/adapters, cinza para infraestrutura e banco.
- Usar setas simples e legiveis.
- Evitar poluicao visual: no maximo 7 grupos grandes e apenas componentes
  essenciais dentro de cada grupo.
- O texto deve estar em portugues.
- Incluir icones/logos pequenos das tecnologias quando possivel, sem deixar o
  diagrama depender deles.

Titulo:
"Arquitetura Completa do IFESDOC"

Subtitulo:
"Sistema de ingestao, indexacao, busca documental, OCR, bot e auditoria"

Grupos principais, da esquerda para a direita:

1. Usuarios e canais
   - Usuarios IFESDOC: admin, servidor, aluno
   - Interface Web
   - Telegram / WhatsApp opcional

2. Frontend - interface-web
   Mostrar com icones de React, TypeScript, Vite e Tailwind.
   Componentes:
   - React SPA
   - AuthContext e rotas protegidas
   - React Query hooks
   - API client
   - Telas: busca, resultados, documento, ingestao, metricas, usuarios
   Setas:
   - Usuarios -> React SPA
   - React SPA -> FastAPI /api/v1

3. API FastAPI - backend/app/api/v1
   Mostrar com icones de Python e FastAPI.
   Componentes:
   - Rotas /api/v1
   - Pydantic schemas
   - JWT Bearer auth
   - Roles: ADMIN e USER
   - Tratamento global de erros
   Setas:
   - FastAPI chama Services

4. Camada de aplicacao - backend/app/services
   Componentes:
   - AuthService
   - DocumentService
   - SearchService
   - IndexService
   - OCRService
   - BotService
   - MetricsService
   - NotificationService
   Mostrar este grupo como o centro do diagrama.

5. Busca, indexacao e padroes de projeto
   Criar dois destaques visuais:

   Destaque A: "Strategy Pattern - usado na busca"
   Conectar SearchService a:
   - Frequency
   - TF-IDF
   - BM25
   - PostgreSQL FTS
   - Semantic
   - Hybrid
   Explicacao curta no proprio destaque:
   "Permite trocar o algoritmo de ranking sem mudar a API."

   Destaque B: "Pipeline Pattern - usado na indexacao"
   Conectar IndexService a uma sequencia horizontal:
   - TextPreprocessStage
   - TextTokenizeStage
   - RelationalIndexPersistStage
   - SemanticEmbeddingPersistStage
   Explicacao curta no proprio destaque:
   "Documento passa por etapas ordenadas ate ficar pesquisavel."

6. Adapters e processamento documental
   Componentes:
   - DocumentAdapterRegistry
   - PDF: pdfplumber
   - DOCX: python-docx
   - TXT / CSV
   - OCR: Tesseract + pytesseract + pdf2image + Pillow
   - EmbeddingAdapter / MockEmbeddingAdapter
   Setas:
   - DocumentService -> Adapters
   - OCRService -> OCR Adapter
   - Adapters -> arquivo/documento processado

7. Dominio, repositorios e persistencia
   Mostrar com icones de SQLAlchemy e PostgreSQL.
   Componentes:
   - Domain models SQLAlchemy
   - Repositories
   - PostgreSQL 16
   - Indice invertido: termo, campo_documento, indice_invertido
   - Full-Text Search: search_vector + GIN + ts_rank_cd + ts_headline
   - Historicos: documento, ingestao, indexacao, busca, OCR, administrativo
   - Feedback de relevancia
   - Document embeddings
   - Volume storage/documents
   Setas:
   - Services -> Repositories -> PostgreSQL
   - DocumentService -> storage/documents

8. Infraestrutura e qualidade
   Componentes:
   - Docker Compose
   - backend container
   - frontend container
   - postgres container
   - notification-worker
   - SonarQube
   - Pytest e Vitest
   Setas:
   - Docker Compose engloba frontend, backend, postgres e worker
   - notification-worker -> NotificationService -> PostgreSQL
   - SonarQube monitora backend e frontend

Fluxos que devem aparecer com setas numeradas ou setas finas:

Fluxo 1 - Login:
Usuario -> React LoginPage -> POST /auth/login -> AuthService -> PostgreSQL -> JWT -> React

Fluxo 2 - Ingestao:
Admin -> Upload -> DocumentService -> Adapter/OCR -> storage -> IndexService -> Pipeline -> PostgreSQL

Fluxo 3 - Busca:
Usuario -> SearchPage -> GET /search -> SearchService -> QueryAnalyzer -> Strategy -> PostgreSQL/indice/embedding -> Resultados

Fluxo 4 - Bot:
Telegram/WhatsApp -> webhook FastAPI -> BotService -> QueryAnalyzer/SearchService -> resposta ao usuario

Requisitos visuais:
- Deixar claro que IFESDOC nao e microservicos; e um monolito modular com
  camadas internas.
- Usar bordas arredondadas leves, sem excesso de sombra.
- Manter no maximo 2 linhas por componente pequeno.
- Colocar uma legenda pequena no rodape:
  "Strategy = troca de ranking | Pipeline = etapas de indexacao | Adapter = isolamento de bibliotecas externas"
- Incluir icones pequenos das tecnologias: React, TypeScript, Vite, Tailwind,
  FastAPI, Python, Pydantic, SQLAlchemy, PostgreSQL, JWT, Docker, Tesseract,
  SonarQube, Pytest, Vitest.
- Nao incluir codigo-fonte, nomes de todos os arquivos, todas as tabelas ou todos
  os endpoints; mostrar apenas o suficiente para explicar a arquitetura.
```

## Prompt alternativo para Mermaid

Use este prompt se a ferramenta gerar diagrama Mermaid:

```text
Gere um diagrama Mermaid flowchart LR para a arquitetura completa do IFESDOC.
Use subgraphs para:
1. Usuarios e canais
2. Frontend React
3. API FastAPI
4. Services
5. Strategy Pattern na busca
6. Pipeline Pattern na indexacao
7. Adapters
8. Repositories, dominio e PostgreSQL
9. Infraestrutura Docker e qualidade

O diagrama deve conter setas principais para login, ingestao, busca e bot. Use
labels curtas em portugues. Nao inclua todos os endpoints nem todas as tabelas.
Inclua estes componentes obrigatorios: React SPA, API client, FastAPI /api/v1,
Pydantic, JWT, AuthService, DocumentService, SearchService, IndexService,
OCRService, BotService, NotificationService, Strategy Pattern, Pipeline Pattern,
DocumentAdapterRegistry, Tesseract OCR, Repositories, SQLAlchemy Domain Models,
PostgreSQL 16, indice invertido, PostgreSQL Full-Text Search com GIN,
storage/documents, notification-worker, Docker Compose e SonarQube.
```

## Checklist de revisao do diagrama

Antes de considerar o diagrama pronto, verificar:

- O titulo identifica claramente o IFESDOC.
- O caminho principal do usuario ate a API esta claro.
- O backend aparece como monolito modular, nao como varios microservicos.
- Strategy Pattern esta ligado ao `SearchService`.
- Pipeline Pattern esta ligado ao `IndexService`.
- PostgreSQL aparece como persistencia, indice invertido e Full-Text Search.
- OCR aparece como fallback para PDF escaneado.
- O frontend mostra React, TypeScript, Vite, Tailwind e React Query.
- A infraestrutura mostra Docker Compose, worker e SonarQube.
- O diagrama pode ser explicado em ate 3 minutos sem depender de termos muito
  especificos.
- Nao ha excesso de setas cruzadas nem componentes pequenos demais para ler.

## Texto curto para apresentar junto do diagrama

```text
O IFESDOC e um monolito modular. O usuario entra pela interface React, que
consome a API FastAPI. A API valida contratos com Pydantic, autentica com JWT e
delega os casos de uso para services. Documentos enviados passam por adapters de
leitura, OCR quando necessario e um pipeline de indexacao. A busca usa um
QueryAnalyzer e troca algoritmos por Strategy Pattern, incluindo PostgreSQL FTS,
BM25, semantica e hibrida. O PostgreSQL guarda documentos, versoes, historicos,
indice invertido, search_vector, feedbacks e metricas. Docker Compose orquestra
frontend, backend, banco e worker, enquanto SonarQube e testes apoiam qualidade.
```
