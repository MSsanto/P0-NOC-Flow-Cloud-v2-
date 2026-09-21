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

O schema é criado/evoluído de forma idempotente pelo Worker:

- `tenants`, incluindo `timezone`, `shift_start_local` e `shift_duration_minutes`;
- `tenant_memberships`;
- `incidents`;
- `incident_events`;
- `handovers`;
- `handover_items`;
- índices tenant/status/severity/timeline/handover.

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
GET  /api/v1/dashboard/summary
GET  /api/v1/handovers/preview
POST /api/v1/handovers
GET  /api/v1/handovers
GET  /api/v1/handovers/latest
GET  /api/v1/handovers/{handover_id}
```

Filtros e paginação preservam os nomes do backend canônico.

## Workers Builds

Configuração do painel:

- Root directory: `apps/web`
- Build command: `npm install --global npm@11 && npm ci && npm run build`
- Deploy command: `npx wrangler deploy`
- Production branch: `main`

Para um D1 novo, o automatic provisioning pode criar o recurso no primeiro deploy.

Para reutilizar um D1 já existente, o `wrangler.jsonc` deve possuir:

```json
{
  "binding": "DB",
  "database_name": "p0-noc-flow-cloud-v2-db",
  "database_id": "<UUID-do-D1-existente>"
}
```

Sem o `database_id`, o Wrangler tenta provisionar outro banco com o mesmo nome e
o deploy falha com `A database with that name already exists`. O database ID não é
segredo, mas precisa corresponder ao recurso correto da conta Cloudflare.

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
- Dashboard e Passagem de Turno funcionam contra o D1 remoto;
- snapshot de handover permanece imutável após normalização do incidente original;
- janela anônima continua bloqueada pelo Access.

## Rollback

Se o adapter Cloudflare falhar:

1. reverter o commit do Worker/D1;
2. o Angular pode voltar a Static Assets-only;
3. manter Access ativo;
4. não apagar o D1 automaticamente;
5. preservar o stack FastAPI/PostgreSQL como referência canônica.
