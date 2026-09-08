# backend

FastAPI backend do **P0 — NOC Flow Cloud v2**.

## Escopo atual — Sprint 1 / EN-003

A fundação executável inclui:

- bootstrap FastAPI sob `/api/v1`;
- settings via `pydantic-settings`;
- SQLAlchemy 2.x e session factory;
- dependency injection de sessão;
- Problem Details compatível com RFC 9457, incluindo `code` estável;
- `X-Request-ID` aceito/gerado e devolvido;
- CORS por allowlist configurável;
- liveness e readiness;
- OpenAPI versionado;
- testes da fundação.

Nenhuma entidade de negócio é criada nesta etapa. Models e migrations permanecem coordenados com **06 Database & Data Model**.

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
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

No Windows:

```powershell
Copy-Item .env.example .env
```

## Endpoints de fundação

- `GET /api/v1/health/live` — processo HTTP está vivo;
- `GET /api/v1/health/ready` — dependências obrigatórias estão prontas (`SELECT 1` no banco);
- `GET /api/v1/docs` — Swagger UI;
- `GET /api/v1/openapi.json` — contrato OpenAPI.

O readiness responde `503 application/problem+json` quando o PostgreSQL não está disponível.

## Testes

```bash
pytest
```

A suíte usa SQLite em memória somente para validar a infraestrutura SQLAlchemy sem exigir PostgreSQL no teste unitário. Development, test integrado, staging e production continuam configurados para PostgreSQL.

## Limites arquiteturais

- domínio/casos de uso não importam FastAPI, SQLAlchemy ou SDK Azure;
- rotas HTTP não recebem regra de negócio;
- módulos compõem seus routers em `app/api/v1/router.py`;
- tenant scoping será obrigatório em repositories de negócio;
- migrations são versionadas e coordenadas com Database & Data Model;
- timestamps persistidos em UTC;
- tokens, secrets e detalhes internos não entram em respostas de erro.
