# Changelog

Este projeto segue a estrutura do Keep a Changelog para registrar incrementos relevantes.

## [Unreleased]

### Added

- fundação documental P0, requisitos, arquitetura e ADRs;
- Angular 22 com shell, routing, tratamento HTTP e fluxo de incidentes;
- FastAPI/Python 3.12 com API versionada `/api/v1`, Problem Details e health checks;
- PostgreSQL 17, SQLAlchemy e Alembic;
- entidades mínimas Tenant e Incident com constraints e índices tenant-scoped;
- US-001 — listagem de incidentes;
- US-002 — criação de incidente;
- US-003 — detalhe de incidente;
- Dockerfiles para frontend/backend e stack Docker Compose com healthchecks;
- GitHub Actions para lint/type-check, testes, migrations, builds, dependency audits e smoke funcional;
- testes de integração HTTP contra PostgreSQL real;
- smoke funcional Nginx → FastAPI → PostgreSQL para criar/listar/detalhar;
- baseline AppSec e headers de segurança do Nginx;
- roteiro de homologação da candidata `v0.1.0-alpha`.

### Fixed

- empacotamento Python/Alembic na fundação backend;
- compatibilidade de Vitest/npm/TypeScript no frontend;
- configuração de testes que substituía PostgreSQL por SQLite no CI;
- gate do Compose antes da existência da infraestrutura;
- inconsistência de validação frontend/backend para strings com espaços e início de incidente no futuro;
- teste de `datetime-local` dependente do timezone do runner.

### Security

- tenant/ator permanecem autoridade server-side e não são aceitos no body de criação;
- CORS usa allowlist;
- containers e proxy recebem baseline de hardening;
- `pip-audit` e `npm audit` fazem parte do pipeline.

### Note

A candidata `v0.1.0-alpha` destina-se a **ambiente local/teste**. OIDC/RBAC ainda não foram implementados e nenhum deploy público/produção está autorizado. Não há tag/GitHub Release publicada neste estágio.
