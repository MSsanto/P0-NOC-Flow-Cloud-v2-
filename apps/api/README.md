# apps/api

Reservado para a API FastAPI do NOC Flow Cloud v2.

**P0:** nenhum código executável deve existir aqui ainda.

## Módulos futuros

- identity;
- tenancy;
- operations;
- incidents;
- communications;
- handover;
- audit;
- integrations;
- observability.

## Regras arquiteturais

- domínio não importa FastAPI/ORM/SDK Azure;
- tenant scoping obrigatório;
- migrations versionadas;
- timestamps UTC;
- OpenAPI sob `/api/v1`;
- logs estruturados e request ID.