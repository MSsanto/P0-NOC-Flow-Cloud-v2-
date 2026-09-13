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
- payloads com campos de autoridade forjados são rejeitados nos fluxos cobertos.

### Note

A candidata atual é `v0.2.0-alpha`, destinada a **ambiente local/teste**. OIDC/RBAC ainda não foram implementados e nenhum deploy público/produção está autorizado. Não há tag/GitHub Release publicada neste estágio.
