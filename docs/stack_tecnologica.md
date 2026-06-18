# Stack Tecnologica do IFESDOC

Este documento resume as tecnologias usadas no IFESDOC e o papel de cada uma na
arquitetura. Para a visao em camadas e o diagrama completo, consulte
`docs/arquitetura.md`.

## Visao geral

O IFESDOC usa uma arquitetura web API-first, com frontend React, backend FastAPI,
PostgreSQL como banco principal e Docker Compose para ambiente local/container.
A busca combina indice invertido relacional, PostgreSQL Full-Text Search,
estrategias de ranking e uma camada preparada para busca semantica.

## Frontend

| Tecnologia | Papel |
| --- | --- |
| React 18 | SPA da interface web |
| TypeScript | Tipagem dos contratos e componentes |
| Vite | Dev server e build do frontend |
| React Router | Rotas publicas e protegidas |
| TanStack React Query | Cache, sincronizacao e ciclo de vida de consultas |
| Tailwind CSS | Estilizacao utilitaria |
| shadcn/ui + Radix UI | Componentes acessiveis e reutilizaveis |
| lucide-react | Icones da interface |
| Recharts | Graficos e visualizacoes |
| Vitest + Testing Library | Testes frontend |

## Backend

| Tecnologia | Papel |
| --- | --- |
| Python | Linguagem principal do backend e pipelines |
| FastAPI | API REST versionada em `/api/v1` |
| Uvicorn | Servidor ASGI |
| Pydantic | Schemas de request/response e validacao |
| pydantic-settings | Configuracoes via ambiente |
| SQLAlchemy | ORM e mapeamento das entidades |
| psycopg2 | Driver PostgreSQL |
| Alembic | Base para versionamento de banco |
| python-jose | Criacao e validacao de JWT |
| passlib + bcrypt | Hash e verificacao de senhas |
| Pytest | Testes unitarios e de integracao |

## Documentos, OCR e busca

| Tecnologia | Papel |
| --- | --- |
| PostgreSQL 16 | Banco relacional, historicos e busca textual |
| PostgreSQL GIN + tsvector | Full-Text Search persistente |
| `ts_rank_cd` / `ts_headline` | Ranking e highlights nativos do PostgreSQL |
| Indice invertido relacional | Estrutura propria com termos, campos e postings |
| pdfplumber | Extracao textual de PDFs |
| python-docx | Extracao textual de DOCX |
| unidecode | Normalizacao textual sem acentos |
| Tesseract OCR | OCR para PDF escaneado |
| pytesseract | Integracao Python com Tesseract |
| pdf2image | Conversao de PDF em imagens para OCR |
| Pillow | Manipulacao de imagens no fluxo OCR |

## Padroes e estrutura

| Padrao / abordagem | Onde aparece |
| --- | --- |
| Monolito modular | API FastAPI unica com camadas internas bem separadas |
| Clean Architecture / DDD simplificado | Separacao entre API, services, domain, repositories e infraestrutura |
| Service Layer | `backend/app/services/` |
| Repository Pattern | `backend/app/repositories/` |
| Strategy Pattern | `backend/app/strategies/`, usado no `SearchService` |
| Pipeline Pattern | `backend/app/pipeline/`, usado no `IndexService` |
| Adapter Pattern | `backend/app/adapters/`, parsers, OCR, bot e embeddings |
| DTO/Schema | `backend/app/schemas/` com Pydantic |

## Infraestrutura

| Tecnologia | Papel |
| --- | --- |
| Docker | Empacotamento do backend e frontend |
| Docker Compose | Orquestracao local de frontend, backend, PostgreSQL, worker e SonarQube |
| PostgreSQL container | Banco principal do IFESDOC |
| Notification worker | Worker Python para alertas e falhas recentes |
| SonarQube Community | Analise estatica e qualidade |
| Volumes Docker | Persistencia de banco, documentos e dados do SonarQube |

## Variaveis e configuracao

Backend:

- `DATABASE_URL`: conexao SQLAlchemy com PostgreSQL.
- `SECRET_KEY`: chave JWT, obrigatoriamente forte.
- `INITIAL_ADMIN_PASSWORD`: senha inicial segura do administrador.
- `BACKEND_CORS_ORIGINS`: origens permitidas do frontend.
- `DOCUMENT_UPLOAD_DIR`: diretorio dos arquivos enviados.
- `DOCUMENT_ALLOWED_EXTENSIONS`: extensoes aceitas.
- `OCR_ENABLED`, `OCR_LANGUAGE`, `OCR_DPI`, `OCR_MAX_PAGES`,
  `OCR_MIN_TEXT_LENGTH`, `OCR_TIMEOUT_SECONDS`: configuracao de OCR.
- `TELEGRAM_BOT_TOKEN`, `WHATSAPP_ACCESS_TOKEN` e variaveis relacionadas:
  integracoes opcionais de bot.

Frontend:

- `VITE_APP_NAME`: nome exibido na interface.
- `VITE_API_URL`: URL da API FastAPI.
- `VITE_USE_MOCK_API`: alterna entre API real e dados mockados.

## Observacao sobre versoes

As versoes efetivas devem ser conferidas nos arquivos de dependencias do modulo
correspondente:

- backend: `backend/requirements.txt`;
- frontend: `interface-web/package.json` e `package-lock.json`.

O arquivo `requirements.txt` na raiz pode representar uma base historica; para o
backend em execucao, prefira `backend/requirements.txt`.
