# Cloudflare Worker + D1 — Private Demo Full-Stack

## Objetivo

Executar a versão privada e funcional do **P0 — NOC Flow Cloud v2** no Worker
`p0-noc-flow-cloud-v2`, mantendo o Cloudflare Access em `All traffic`.

Este ambiente é **demo/staging privado**, não produção.

## Arquitetura

```text
Browser
  ↓
Cloudflare Access
  ↓
p0-noc-flow-cloud-v2.workers.dev
  ├─ Angular / Static Assets
  └─ /api/v1 → Worker API
                 ↓
                 D1
```

O stack canônico FastAPI + PostgreSQL permanece preservado no diretório
`backend/`. O Worker API é um adapter operacional para o private demo.

## Segurança

A API:

1. exige `Cf-Access-Jwt-Assertion`;
2. valida JWT RS256 contra os JWKS do issuer Cloudflare Access;
3. valida expiração/not-before;
4. usa a identidade autenticada como ator;
5. resolve role pela membership D1;
6. aplica permissions no servidor;
7. inclui `tenant_id` em todas as queries;
8. não aceita `tenant_id`, ator, ID ou timestamps como autoridade do cliente.

O primeiro usuário que já passou pelo Access é bootstrapado como Admin somente
quando o tenant ainda não possui nenhuma membership. Depois disso, outras
identidades são negadas até existir membership explícita.

## D1

A binding `DB` é declarada sem `database_id` no repositório. O Wrangler usa
automatic provisioning no primeiro deploy remoto.

O schema é criado de forma idempotente pelo Worker:

- `tenants`;
- `tenant_memberships`;
- `incidents`;
- `incident_events`;
- índices tenant/status/severity/timeline.

Somente dados sintéticos de demonstração são permitidos.

## Contrato disponível

```text
GET  /api/v1/auth/me
GET  /api/v1/health/live
GET  /api/v1/health/ready
GET  /api/v1/incidents
GET  /api/v1/incidents/query
POST /api/v1/incidents
GET  /api/v1/incidents/{id}
POST /api/v1/incidents/{id}/updates
POST /api/v1/incidents/{id}/normalize
GET  /api/v1/incidents/{id}/timeline
```

Filtros e paginação preservam os nomes do backend canônico.

## Workers Builds

Configuração do painel:

- Root directory: `apps/web`
- Build command: `npm install --global npm@11 && npm ci && npm run build`
- Deploy command: `npx wrangler deploy`
- Production branch: `main`

Não é necessário cadastrar o D1 manualmente quando o automatic provisioning
funciona no Build; o binding é criado no deploy.

## Gates

Antes de homologar:

- Angular type-check;
- Angular tests;
- Worker contract tests;
- Angular production build;
- Wrangler full-stack dry run;
- CI geral;
- smoke Docker canônico;
- deploy Cloudflare verde;
- `/api/v1/auth/me` retorna Admin para o usuário bootstrap;
- criação/listagem/detalhe/update/timeline/normalização funcionam;
- janela anônima continua bloqueada pelo Access.

## Rollback

Se o adapter Cloudflare falhar:

1. reverter o commit do Worker/D1;
2. o Angular pode voltar a Static Assets-only;
3. manter Access ativo;
4. não apagar o D1 automaticamente;
5. preservar o stack FastAPI/PostgreSQL como referência canônica.
