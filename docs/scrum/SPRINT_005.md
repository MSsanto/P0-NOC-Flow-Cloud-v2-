# Sprint 005 — Auditoria & Observabilidade

**Status:** Ready para implementação  
**Duração planejada:** 2 semanas  
**Release alvo:** `v0.5.0-rc1`  
**Sprint Goal:** tornar ações críticas rastreáveis e requests correlacionáveis sem registrar conteúdo sensível.

## US-014 — Consultar trilha de auditoria [P1]

Como administrador/supervisor, quero consultar ações relevantes para investigar alterações e reconstruir eventos operacionais.

**Responsável primário:** 05 Backend & API

### Critérios de aceite

1. auditoria é append-only no fluxo HTTP suportado;
2. cada evento contém tenant, ator, ação, tipo/id do recurso, timestamp e request ID;
3. auditoria não armazena body, token, observações ou mensagem operacional livre;
4. criação, atualização e normalização de incidente são auditadas na mesma transação da mudança;
5. finalização de handover é auditada na mesma transação;
6. leitura é tenant-scoped;
7. Admin e Supervisor possuem `audit:read`; Operator e Viewer recebem 403;
8. endpoint suporta paginação e filtros por ação/tipo de recurso;
9. recursos de outro tenant não entram no resultado;
10. não existem endpoints HTTP de update/delete da auditoria.

## EN-S5-01 — Observabilidade & Resiliência [P0]

### Critérios de aceite

1. todo request recebe ou propaga `X-Request-ID`;
2. a resposta expõe o mesmo `X-Request-ID`;
3. log estruturado por request contém timestamp, level, request_id, método, path, status e duração;
4. logs não registram Authorization, Cookie, query sensível ou body;
5. exceção inesperada gera log correlacionável sem stack trace enviado ao cliente;
6. `/health/live` não depende de banco;
7. `/health/ready` retorna 503 quando PostgreSQL obrigatório está indisponível;
8. implementação permanece provider-neutral e compatível com OpenTelemetry/Application Insights;
9. CI valida correlação, redaction e health;
10. Application Insights real fica para Sprint 6/Azure, evitando acoplamento prematuro.

## Modelo de dados

Nova tabela `audit_events`:

| Campo | Regra |
|---|---|
| id | UUID PK |
| tenant_id | UUID NOT NULL, FK tenants |
| actor_subject | varchar(255) NOT NULL |
| action | varchar(64) NOT NULL |
| resource_type | varchar(64) NOT NULL |
| resource_id | UUID nullable |
| request_id | varchar(128) NOT NULL |
| occurred_at | timestamptz NOT NULL |

Índices:

- tenant + occurred_at desc;
- tenant + action + occurred_at desc;
- tenant + resource_type + resource_id.

Retenção da RC: sem purge automático. Política de retenção de produção deve ser definida antes da v1.0.

## RBAC

- `audit:read`: Admin, Supervisor.
- Operator e Viewer não consultam trilha de auditoria.

## Segurança

Nunca persistir/logar:

- Authorization/JWT;
- Cookie;
- request/response body;
- sintomas;
- mensagem de update;
- nota de normalização;
- observações do handover;
- connection string/secrets.

## Gates

- Ruff;
- Alembic + PostgreSQL real;
- pytest;
- OpenAPI;
- RBAC/cross-tenant;
- atomicidade da auditoria;
- request ID propagation/sanitization;
- redaction de logging;
- health live/ready;
- regressão Sprint 2 e Sprint 4;
- dependency audits;
- review independente.

## Tasks

- [x] TASK-ARC-S5-01 padrão de auditoria/observabilidade;
- [x] TASK-DB-S5-00 schema/índices planejados;
- [x] TASK-SEC-S5-00 permissions e dados proibidos definidos;
- [x] TASK-QA-S5-00 matriz de cenários definida;
- [ ] TASK-BE-S5-01 audit trail;
- [ ] TASK-BE-S5-02 correlation/logging estruturado;
- [ ] TASK-BE-S5-03 health/resiliência;
- [ ] TASK-DB-S5-01 migration audit/index review;
- [ ] TASK-FE-S5-01 visualização autorizada da auditoria;
- [ ] TASK-QA-S5-01 failure scenarios/regressão;
- [ ] TASK-SEC-S5-01 AppSec formal;
- [ ] TASK-DOC-S5-01 runbook/troubleshooting;
- [ ] TASK-CR-S5-01 review independente;
- [ ] TASK-REL-S5-01 homologação.

## Fora do escopo

- Azure Application Insights real;
- Grafana/Prometheus;
- tracing distribuído externo;
- alertas/SLOs de produção;
- exportação de auditoria;
- purge job.
