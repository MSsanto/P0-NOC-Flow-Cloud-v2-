# backend

FastAPI backend do **P0 — NOC Flow Cloud v2**.

## Escopo atual — Sprint 1 / EN-002 + EN-003

A fundação executável inclui:

- bootstrap FastAPI sob `/api/v1`;
- settings via `pydantic-settings`;
- SQLAlchemy 2.x e session factory;
- models iniciais `Tenant` e `Incident`;
- Alembic com migration inicial versionada;
- dependency injection de sessão;
- Problem Details compatível com RFC 9457, incluindo `code` estável;
- `X-Request-ID` aceito/gerado e devolvido;
- CORS por allowlist configurável;
- liveness e readiness;
- OpenAPI versionado;
- testes da fundação.

O schema da Sprint 1 é deliberadamente mínimo: `tenants` + `incidents`. Identidade completa, memberships, sites, severidades configuráveis e timeline entram somente nas histórias posteriores aprovadas.

## Requisitos

- Python 3.12+
- PostgreSQL

## Setup local

```bash
cd backend
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\\Scripts\\Activate.ps1

pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

No Windows:

```powershell
Copy-Item .env.example .env
alembic upgrade head
```

## Migrations

Aplicar todas as migrations:

```bash
alembic upgrade head
```

Consultar estado atual:

```bash
alembic current
alembic history
```

Downgrade da migration inicial é permitido para ambiente local/teste descartável:

```bash
alembic downgrade base
```

Em ambientes com dados reais, mudanças destrutivas devem seguir expand/contract e preferir correção forward; downgrade não é estratégia automática de rollback de dados.

## Endpoints de fundação

- `GET /api/v1/health/live` — processo HTTP está vivo;
- `GET /api/v1/health/ready` — dependências obrigatórias estão prontas (`SELECT 1` no banco);
- `GET /api/v1/docs` — Swagger UI;
- `GET /api/v1/openapi.json` — contrato OpenAPI.

O readiness responde `503 application/problem+json` quando o PostgreSQL não está disponível.

## Testes

```bash
pytest
ruff check app tests
```

A suíte unitária pode usar SQLite em memória apenas para infraestrutura que não dependa de comportamento específico do PostgreSQL. Migrations, constraints e repositories da integração devem ser validados com PostgreSQL real/container antes da conclusão da Sprint.

## Limites arquiteturais

- domínio/casos de uso não importam FastAPI, SQLAlchemy ou SDK Azure;
- rotas HTTP não recebem regra de negócio;
- módulos compõem seus routers em `app/api/v1/router.py`;
- tenant scoping é obrigatório em repositories de negócio;
- migrations são versionadas e coordenadas com Database & Data Model;
- IDs públicos iniciais usam UUID4 gerado na aplicação, sem extensão PostgreSQL;
- timestamps persistidos em UTC;
- tokens, secrets e detalhes internos não entram em respostas de erro.
