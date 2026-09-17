# Changelog

Este projeto segue a estrutura do Keep a Changelog para registrar incrementos relevantes.

## [Unreleased]

### Added

- fundação documental P0, requisitos, arquitetura e ADRs;
- Angular 22 com shell, routing, tratamento HTTP e fluxo de incidentes;
- FastAPI/Python 3.12 com API versionada `/api/v1`, Problem Details e health checks;
- PostgreSQL 17, SQLAlchemy e Alembic;
- entidades Tenant e Incident com constraints e índices tenant-scoped;
- US-001 — listagem de incidentes;
- US-002 — criação de incidente;
- US-003 — detalhe de incidente;
- US-004 — atualizações operacionais de incidentes ativos;
- US-005 — normalização de incidente com transição para `RESOLVED` e confirmação UX;
- US-006 — timeline append-only com eventos `INCIDENT_CREATED`, `INCIDENT_UPDATED` e `INCIDENT_NORMALIZED`;
- US-007 — filtros por status/severidade/período, paginação e ordenação;
- `GET /api/v1/incidents/query` para consulta avançada, preservando `GET /api/v1/incidents` retrocompatível;
- Dockerfiles para frontend/backend e stack Docker Compose com healthchecks;
- GitHub Actions para lint/type-check, testes, migrations, builds, dependency audits e smoke funcional;
- smoke específico da Sprint 2 atravessando Nginx → FastAPI → PostgreSQL;
- testes de integração HTTP contra PostgreSQL real;
- baseline AppSec e headers de segurança do Nginx;
- autenticação por OIDC/JWT com validação de issuer, audience, assinatura e claims obrigatórias;
- integração da demo privada com Cloudflare Access;
- RBAC server-side com Admin, Supervisor, Operator e Viewer;
- memberships internas e isolamento cross-tenant;
- endpoint autenticado `GET /api/v1/auth/me`;
- terceira migration Alembic para usuários e memberships;
- testes unitários e de integração de autenticação, permissões e isolamento por tenant.
- roteiros reproduzíveis de homologação das candidatas `v0.1.0-alpha` e `v0.2.0-alpha`.

### Fixed

- empacotamento Python/Alembic na fundação backend;
- compatibilidade de Vitest/npm/TypeScript no frontend;
- configuração de testes que substituía PostgreSQL por SQLite no CI;
- gate do Compose antes da existência da infraestrutura;
- inconsistência de validação frontend/backend para strings com espaços e início de incidente no futuro;
- teste de `datetime-local` dependente do timezone do runner;
- ordenação de persistência SQLAlchemy para garantir que o incidente pai seja materializado antes do primeiro evento;
- registro inicialmente implícito da rota de consulta da Sprint 2, substituído por inclusão explícita do router no app.

### Security

- tenant/ator permanecem autoridade server-side e não são aceitos nos bodies operacionais;
- recursos e eventos são consultados tenant-scoped;
- atualização de incidente `RESOLVED/CLOSED` é bloqueada com conflito de estado;
- segunda normalização é bloqueada;
- CORS usa allowlist;
- containers e proxy recebem baseline de hardening;
- `pip-audit` e `npm audit` fazem parte do pipeline;
- payloads com campos de autoridade forjados são rejeitados nos fluxos cobertos;
- tokens OIDC inválidos, memberships ausentes e tentativas cross-tenant retornam 401/403 sem confiar em autorização do frontend.

### Note

A candidata atual é `v0.3.0-beta`, destinada a ambiente local e demo privada protegida por Cloudflare Access/OIDC. OIDC, RBAC e isolamento multi-tenant estão implementados e validados no CI; nenhum deploy público/produção está autorizado. Não há tag/GitHub Release publicada neste estágio.
