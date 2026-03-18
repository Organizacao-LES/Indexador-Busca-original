# Arquitetura do Frontend (`interface-web`)

## Visão geral

O frontend do IFESDOC é uma SPA construída com React 18, TypeScript e Vite. A aplicação foi organizada para operar em dois modos:

- `mock-first`: a interface funciona mesmo sem backend completo, usando `mock-data.ts`.
- `API real`: a mesma camada de serviços troca o mock por chamadas HTTP para a API FastAPI.

Arquiteturalmente, o frontend adota uma separação simples entre:

- composição global da aplicação;
- navegação e proteção de rotas;
- estado de autenticação;
- acesso a dados por serviços e hooks;
- páginas de negócio;
- biblioteca visual reutilizável.

## Fluxo arquitetural

```text
main.tsx
  -> App.tsx
    -> QueryClientProvider
    -> AuthProvider
    -> TooltipProvider / Toasters
    -> BrowserRouter
      -> ProtectedRoute
        -> AppLayout
          -> AppSidebar
          -> AppHeader
          -> Pages
            -> hooks/use-app-query
              -> lib/api/services
                -> lib/api/client
                -> lib/api/mock-data
```

## Stack e responsabilidades

- `React 18`: renderização declarativa e composição de componentes.
- `TypeScript`: tipagem dos contratos da interface e da API.
- `Vite`: build, dev server e resolução de módulos.
- `React Router DOM`: roteamento da SPA.
- `@tanstack/react-query`: cache, sincronização e ciclo de vida de consultas remotas.
- `Tailwind CSS`: estilização utilitária e tokens visuais.
- `shadcn/ui` + `Radix UI`: base dos componentes reutilizáveis.
- `Vitest` + Testing Library: testes unitários do frontend.

## Estrutura de diretórios e função de cada pacote

### Raiz `interface-web/`

- `package.json`: define dependências, scripts de build, lint e testes.
- `vite.config.ts`: configura Vite, alias `@`, porta `8080` e plugin React SWC.
- `tailwind.config.ts`: centraliza tokens, cores semânticas, animações e tema.
- `postcss.config.js`: integra Tailwind ao pipeline CSS.
- `components.json`: configura o ecossistema `shadcn/ui` e os aliases de código.
- `tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json`: tipagem e compilação TypeScript.
- `eslint.config.js`: regras de lint.
- `vitest.config.ts`: configuração dos testes.
- `index.html`: ponto de montagem da SPA no DOM.
- `.env.example`: variáveis de ambiente do frontend.
- `README.md`: guia operacional do módulo frontend.
- `public/`: ativos estáticos servidos sem transformação.
- `src/`: código-fonte da aplicação.
- `dist/`: saída de build gerada pelo Vite.
- `node_modules/`: dependências instaladas localmente.

### `public/`

- `favicon.ico`: ícone da aplicação.
- `robots.txt`: instruções para crawlers.
- `placeholder.svg`: ativo visual auxiliar.

### `src/`

É o núcleo da aplicação. Reúne bootstrap, layout, páginas, acesso a dados, contexto, hooks e componentes.

#### `src/main.tsx`

- ponto de entrada da SPA;
- monta `App` dentro de `#root`;
- ativa `StrictMode`.

#### `src/App.tsx`

É o orquestrador global do frontend.

Responsabilidades:

- cria o `QueryClient`;
- injeta `QueryClientProvider`;
- injeta `AuthProvider`;
- injeta providers transversais de UI (`Tooltip`, `Toaster`, `Sonner`);
- define o roteamento principal;
- separa rotas públicas (`/login`) de rotas protegidas;
- aplica `AppLayout` às telas autenticadas.

#### `src/index.css`

Folha global do frontend.

Responsabilidades:

- importar camadas base do Tailwind;
- definir variáveis CSS do tema;
- registrar classes utilitárias específicas do projeto, como estilos de cartões, sidebar e estados visuais.

#### `src/App.css`

- CSS complementar local;
- concentra ajustes visuais adicionais fora do escopo do tema global.

### `src/components/`

Contém componentes compostos da aplicação, mais próximos do domínio da interface do que da biblioteca visual genérica.

#### `src/components/AppLayout.tsx`

- layout principal das rotas autenticadas;
- combina `AppSidebar`, `AppHeader` e `Outlet`;
- define a estrutura shell da aplicação.

#### `src/components/AppSidebar.tsx`

- navegação lateral persistente;
- lista as áreas funcionais do sistema;
- controla logout via `AuthContext`;
- usa `appEnv.appName` para branding da instância.

#### `src/components/AppHeader.tsx`

- cabeçalho superior do shell autenticado;
- oferece busca rápida;
- exibe estado de sessão do usuário autenticado;
- concentra ações globais de topo.

#### `src/components/ProtectedRoute.tsx`

- guarda de rota;
- bloqueia acesso sem autenticação;
- mostra estado de carregamento da sessão;
- redireciona para `/login` preservando a rota de origem.

#### `src/components/NavLink.tsx`

- componente auxiliar de navegação;
- padroniza links internos com estados visuais.

#### `src/components/PageState.tsx`

- abstrai estados padrão de tela;
- evita repetição de loaders e mensagens de erro.

### `src/components/ui/`

É a biblioteca de componentes de interface reutilizáveis. A maioria dos arquivos é baseada em `shadcn/ui` e `Radix UI`, servindo como camada de apresentação padronizada.

Função arquitetural do pacote:

- padronizar botões, inputs, modais, tabelas, seletores e feedback visual;
- reduzir duplicação de markup e estilo;
- desacoplar páginas das primitivas de baixo nível.

Subgrupos lógicos:

- entrada e formulário: `input.tsx`, `textarea.tsx`, `checkbox.tsx`, `radio-group.tsx`, `select.tsx`, `switch.tsx`, `slider.tsx`, `input-otp.tsx`, `form.tsx`, `label.tsx`.
- navegação e estrutura: `tabs.tsx`, `breadcrumb.tsx`, `pagination.tsx`, `menubar.tsx`, `navigation-menu.tsx`, `sidebar.tsx`, `sheet.tsx`, `drawer.tsx`, `resizable.tsx`, `scroll-area.tsx`.
- feedback e overlays: `toast.tsx`, `toaster.tsx`, `sonner.tsx`, `tooltip.tsx`, `alert.tsx`, `alert-dialog.tsx`, `dialog.tsx`, `popover.tsx`, `hover-card.tsx`.
- visualização de dados: `table.tsx`, `card.tsx`, `badge.tsx`, `avatar.tsx`, `progress.tsx`, `skeleton.tsx`, `chart.tsx`, `calendar.tsx`, `carousel.tsx`.
- comandos e interação contextual: `command.tsx`, `context-menu.tsx`, `dropdown-menu.tsx`, `accordion.tsx`, `collapsible.tsx`, `toggle.tsx`, `toggle-group.tsx`, `separator.tsx`, `aspect-ratio.tsx`.
- utilitários de notificação: `use-toast.ts`.

Observação arquitetural:

- `src/components/ui/sidebar.tsx` é uma infraestrutura visual genérica de sidebar, enquanto `src/components/AppSidebar.tsx` implementa a navegação do domínio IFESDOC sobre essa base conceitual.

### `src/contexts/`

#### `src/contexts/AuthContext.tsx`

É a camada de estado global de autenticação.

Responsabilidades:

- ler e persistir a sessão no `localStorage`;
- expor `user`, `isAuthenticated`, `isLoading`, `login` e `logout`;
- integrar a autenticação à camada de serviços (`authService`);
- sustentar proteção de rotas e informações de sessão no layout.

### `src/hooks/`

Pacote de hooks compartilhados.

#### `src/hooks/use-app-query.ts`

- centraliza hooks de leitura baseados em `react-query`;
- encapsula `queryKey`, `queryFn`, políticas de atualização e cache;
- fornece hooks especializados por domínio, como `useUsers`, `useMetrics`, `useDocument`, `useSearchResults`.

#### `src/hooks/use-toast.ts`

- hook de notificação visual;
- integra componentes e páginas ao sistema de toast.

#### `src/hooks/use-mobile.tsx`

- hook utilitário para responsividade;
- detecta comportamento/estado voltado a layouts móveis.

### `src/lib/`

Camada de utilidades transversais e acesso a dados.

#### `src/lib/env.ts`

- resolve variáveis de ambiente do frontend;
- controla `apiBaseUrl`, `useMockApi` e `appName`.

#### `src/lib/storage.ts`

- centraliza chaves de persistência do `localStorage`;
- evita strings mágicas espalhadas.

#### `src/lib/utils.ts`

- utilitários genéricos compartilhados;
- normalmente usado para concatenação de classes e helpers leves.

#### `src/lib/api/`

É a camada de integração do frontend com o backend ou com dados simulados.

##### `src/lib/api/client.ts`

- cliente HTTP base;
- compõe URL com query string;
- injeta headers e token;
- normaliza tratamento de erro via `ApiError`;
- abstrai `fetch` para consumo consistente.

##### `src/lib/api/services.ts`

- camada de serviço por domínio funcional;
- expõe `authService`, `searchService`, `documentService`, `userService`, `ingestionService`, `indexService`, `metricsService`, `historyService`, `settingsService`;
- decide entre mock e API real;
- concentra os endpoints REST esperados pela interface.

##### `src/lib/api/mock-data.ts`

- base mockada de dados de sessão, busca, métricas, usuários, histórico, ingestão e configurações;
- permite desenvolver o frontend antes da consolidação completa do backend REST.

### `src/pages/`

Camada de páginas roteáveis. Cada arquivo representa uma área funcional da aplicação.

#### `src/pages/LoginPage.tsx`

- tela pública de autenticação;
- usa `AuthContext`;
- redireciona o usuário para a rota originalmente solicitada após login.

#### `src/pages/SearchPage.tsx`

- tela inicial de busca;
- captura consulta principal;
- exibe filtros avançados;
- mostra histórico de buscas recentes.

#### `src/pages/ResultsPage.tsx`

- apresenta os resultados paginados da busca;
- lê query string da URL;
- usa `useSearchResults`;
- permite navegação para o documento detalhado.

#### `src/pages/DocumentViewPage.tsx`

- visualização detalhada de documento;
- exibe metadados, conteúdo e ações como reindexação e download;
- consome `useDocument`.

#### `src/pages/IngestionPage.tsx`

- módulo de ingestão;
- representa upload individual, lote e histórico;
- simula o pipeline operacional de validação, extração e indexação.

#### `src/pages/IndexStatusPage.tsx`

- observabilidade da indexação;
- apresenta progresso, resumo de execução, taxa de sucesso e logs operacionais.

#### `src/pages/MetricsPage.tsx`

- dashboard analítico;
- usa gráficos e indicadores para consultas, termos mais buscados e distribuição documental.

#### `src/pages/HistoryPage.tsx`

- auditoria operacional;
- lista eventos por data, usuário, ação e status.

#### `src/pages/UsersPage.tsx`

- gestão administrativa de usuários;
- permite visualizar, ativar/inativar, criar e editar perfis no nível de interface.

#### `src/pages/SettingsPage.tsx`

- configurações da instância;
- persiste preferências operacionais e parâmetros do frontend.

#### `src/pages/NotFound.tsx`

- fallback para rotas não mapeadas;
- trata navegação inválida.

#### `src/pages/Index.tsx`

- página residual de template;
- atualmente não participa do fluxo principal da aplicação.

### `src/types/`

#### `src/types/app.ts`

- contrato tipado do frontend;
- define modelos de usuário, sessão, busca, documento, ingestão, métricas, histórico e configurações;
- funciona como fronteira tipada entre UI e camada de serviço.

### `src/test/`

#### `src/test/setup.ts`

- bootstrap do ambiente de testes frontend.

#### `src/test/example.test.ts`

- teste básico de exemplo;
- evidencia que a estrutura de testes já está preparada, mas ainda com cobertura inicial.

## Como as camadas se relacionam

### 1. Bootstrap e infraestrutura

- `main.tsx` inicializa a aplicação.
- `App.tsx` injeta providers e rotas.
- `vite.config.ts` e `tailwind.config.ts` sustentam o runtime e a camada visual.

### 2. Sessão e acesso

- `AuthContext` mantém sessão persistida.
- `ProtectedRoute` protege a navegação.
- `AppHeader` e `AppSidebar` refletem o estado autenticado.

### 3. Dados

- páginas chamam hooks de `use-app-query`;
- hooks chamam `services.ts`;
- `services.ts` decide entre `mock-data.ts` e `client.ts`;
- `client.ts` centraliza o HTTP.

### 4. Apresentação

- páginas descrevem o comportamento de cada caso de uso;
- `components/` organiza o layout do produto;
- `components/ui/` oferece os blocos visuais reutilizáveis.

## Características arquiteturais relevantes

- forte desacoplamento entre páginas e transporte HTTP;
- fallback mockado como estratégia de desenvolvimento incremental;
- cache e sincronização centralizados em React Query;
- autenticação simples orientada a sessão em `localStorage`;
- shell administrativo único para todas as áreas autenticadas;
- biblioteca de UI compartilhada para consistência visual.

## Limitações e estado atual

- a integração REST prevista em `services.ts` depende de endpoints que ainda não estão implementados integralmente no backend;
- parte das ações das páginas ainda simula comportamento com `toast`, `setTimeout` e mocks;
- existe uma base robusta de interface, mas a consolidação final depende da convergência com a API FastAPI.
