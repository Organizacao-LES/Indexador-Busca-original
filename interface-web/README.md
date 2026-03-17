# IFESDOC Frontend

Frontend React do sistema IFESDOC. Esta interface foi reorganizada para funcionar como base definitiva da aplicação, com:

- autenticação local persistida
- proteção de rotas
- cliente de API centralizado
- hooks com React Query
- fallback mockado enquanto o backend REST ainda é consolidado

## Executar localmente

```sh
cd interface-web
npm install
npm run dev
```

O Vite sobe por padrão na porta `8080`.

## Variáveis de ambiente

Copie `interface-web/.env.example` para `interface-web/.env` e ajuste conforme o estágio do projeto:

```env
VITE_APP_NAME=IFESDOC
VITE_API_URL=http://localhost:8000
VITE_USE_MOCK_API=true
```

### Modo mock

Com `VITE_USE_MOCK_API=true`, a interface funciona sem backend completo. Isso permite evoluir navegação, UX, formulários e integração de páginas agora.

### Modo API real

Quando as rotas forem implementadas no backend, altere para:

```env
VITE_USE_MOCK_API=false
```

e mantenha `VITE_API_URL` apontando para a API FastAPI.

## Estrutura relevante

- `src/contexts/AuthContext.tsx`: sessão e autenticação.
- `src/lib/api/client.ts`: cliente HTTP comum.
- `src/lib/api/services.ts`: serviços por domínio.
- `src/lib/api/mock-data.ts`: dados de fallback.
- `src/hooks/use-app-query.ts`: hooks de consulta compartilhados.
- `src/pages/`: telas ligadas à camada de dados.
