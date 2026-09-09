# ADR-0007 — UUID4 na aplicação e Alembic para migrations

**Status:** Accepted  
**Data:** 2026-09-08

## Contexto

A Sprint 1 precisa materializar o schema PostgreSQL sem depender de extensões específicas do banco e precisa de migrations reproduzíveis compatíveis com FastAPI + SQLAlchemy.

## Decisão

- usar Alembic como mecanismo de migrations do backend;
- usar `uuid` como tipo persistido para IDs públicos;
- gerar UUID4 na aplicação com `uuid.uuid4()` na fase inicial;
- não exigir `uuid-ossp`, `pgcrypto` ou outra extensão PostgreSQL apenas para gerar IDs;
- manter migrations explícitas, versionadas e revisáveis;
- validar migrations dependentes de comportamento PostgreSQL contra PostgreSQL real/container, não substituir essa validação por SQLite.

## Consequências positivas

- setup local/cloud mais simples;
- nenhum requisito de extensão no PostgreSQL;
- models e migrations usam tipos suportados pelo SQLAlchemy;
- IDs podem ser gerados antes do flush quando necessário;
- estratégia pode evoluir para UUIDv7/ULID posteriormente por ADR/migration se existir benefício comprovado.

## Trade-offs

- UUID4 não preserva ordenação temporal no próprio identificador;
- índices de PK podem ter menor localidade que identificadores monotônicos;
- SQLite não reproduz todas as constraints/funções do PostgreSQL e permanece inadequado para validar migrations de integração.

## Alternativas consideradas

- UUID gerado por extensão PostgreSQL: rejeitado inicialmente por adicionar dependência operacional sem benefício necessário para o MVP;
- ULID/UUIDv7: possível evolução futura, mas complexidade prematura para a Sprint 1;
- integer autoincrement: simples, porém menos adequado a identificadores públicos e evolução distribuída futura.
