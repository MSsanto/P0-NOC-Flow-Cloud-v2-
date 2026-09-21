# Matriz de rastreabilidade

Objetivo: provar que requisitos essenciais possuem trabalho planejado e, quando já implementados, evidência executável correspondente.

| Requisito | Backlog principal | Evidência |
|---|---|---|
| RF-001 Autenticação | P1-004 / Sprint 3 | `test_auth_security.py`, `test_cloudflare_access.py`, `GET /api/v1/auth/me` |
| RF-002 Tenant authz | P1-005 / Sprint 3 | `test_auth_memberships.py`, `test_cloudflare_access_membership.py` |
| RF-003 Papéis | Sprint 3 / Sprint 4 | permissões atuais de incidente + extensão planejada `handover:read`/`handover:finalize` |
| RF-004 Base operacional | P1-006/P2-004 | CRUD integration |
| RF-005 Incidente | P1-007 | domain + API integration |
| RF-006 Correlação | P2-005 | unit + cenários de janela |
| RF-007 Timeline | P1-007/P2-001 / Sprint 2 | testes de API/integração e ausência de endpoints update/delete de evento |
| RF-008 Atualização | P2-002 / Sprint 2 | `test_incidents_api.py` + Sprint 2 Functional Smoke |
| RF-009 Normalização | P2-006 / Sprint 2 | `test_incidents_api.py` + Sprint 2 Functional Smoke |
| RF-010 Reabertura | P2-007 | permission/state tests |
| RF-011 Templates | P2-008/P2-009 | snapshot/version tests |
| RF-012 Handover | P2-012/P2-013 / Sprint 4 | ADR-0008 + APIs de preview/finalize/history/latest/by-id + integration tests + Sprint 4 Functional Smoke |
| RF-013 Busca | P2-011 | query integration |
| RF-014 Dashboard | P2-010 / Sprint 4 | `/dashboard/summary` + frontend Dashboard + integration tests + Sprint 4 Functional Smoke |
| RF-015 Auditoria | P2-014 | audit transaction tests |
| RF-016 Exportação | P2-016 | authz + audit |
| RF-017 Demo sintética | P2-019 | public-data validation |
| RF-018 API versionada | P1 | `test_openapi.py` + endpoints sob `/api/v1` |
| RNF-002 Isolamento | P1-005 / Sprint 3 / Sprint 4 | testes negativos cross-tenant em memberships, incidentes, dashboard e handover |
| RNF-005 Acessibilidade | P2-018 | automated + keyboard manual |
| RNF-007 Observabilidade | P1/P3 | request-id/health/metrics checks |

## Uso

Ao alterar um requisito:

1. atualizar `02-REQUIREMENTS.md`;
2. revisar backlog afetado;
3. revisar testes esperados;
4. criar ADR se houver mudança arquitetural;
5. atualizar esta matriz.

## Baseline de governança — 21/09/2026

Commit de referência: `907f743d048df9b47b1c22682b3a21b91b4cb764`.

Gates oficiais verificados no `main`:

- CI — success;
- Sprint 2 Functional Smoke — success;
- Private Demo Compose — success;
- Cloudflare Private UI — success.

O CI confirmou lint backend, migrations PostgreSQL, testes backend, audit Python, readiness da API, type-check frontend, unit tests, build de produção, audit npm e compose smoke.

## Rastreabilidade do readiness — Sprint 4

| Story | Requisito | Decisão/contrato | Evidência planejada |
|---|---|---|---|
| US-011 Dashboard operacional | RF-014, RNF-002, RNF-005 | `06-API-CONTRACT.md`, `07-UX-FLOWS.md` | unit/integration de agregação, cross-tenant, frontend states |
| US-012 Criar passagem | RF-012, RF-003, RNF-002, RNF-008 | ADR-0008, `05-DATA-MODEL.md`, `06-API-CONTRACT.md`, `08-SECURITY-PRIVACY.md` | transaction rollback, version conflict, Viewer 403, forged authority 422 |
| US-013 Consultar passagem | RF-012, RF-003, RNF-002 | ADR-0008, `06-API-CONTRACT.md`, `07-UX-FLOWS.md` | latest/by-id, historical immutability, cross-tenant 404, Viewer read |

### Baseline de entrada da Sprint 4

Commit: `e9bf9d4f66337117860160e81e01f27754e84c63`.

Em 21/09/2026, após merge da sincronização normativa da Sprint 3:

- CI: success;
- backend lint/migration/tests/pip-audit/readiness: success;
- frontend type-check/unit/build/npm-audit: success;
- compose smoke: success;
- Sprint 2 Functional Smoke: success;
- Private Demo Compose: success.


## Evidência de implementação — Sprint 4

Branch de implementação: `feat/sprint4-dashboard-handover`.

Principais artefatos:

- migration `20260921_0004_shift_handovers.py`;
- módulo `backend/app/modules/operations/`;
- componentes Angular `dashboard-page.component.ts` e `handover-page.component.ts`;
- testes `test_shift_window.py` e `test_operations_api.py`;
- workflow `sprint4-smoke.yml`.

Gates do PR de implementação: CI, Frontend Foundation, Cloudflare Private UI, Private Demo Compose, Sprint 2 Functional Smoke e Sprint 4 Functional Smoke.
