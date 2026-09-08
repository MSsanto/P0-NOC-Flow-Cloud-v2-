# Plano de implementação após aprovação do P0

> Este documento não autoriza o início do código. Ele define a ordem para quando o P0 for aprovado.

## Estratégia

Construir por **fatias verticais**, evitando criar todo o banco, depois toda a API e só depois o front-end.

## Incremento 1 — Fundação executável

Entregas:

- scaffold `apps/api` e `apps/web`;
- PostgreSQL local;
- migrations;
- `/health/live` e `/health/ready`;
- CI de lint/test/build;
- configuração por env;
- logging/request ID.

Saída: aplicação vazia, mas executável e testável.

## Incremento 2 — Identity + tenant

- identidade de desenvolvimento controlada;
- entidades user/tenant/membership;
- endpoint `/me` e `/me/tenants`;
- middleware/dependency de contexto;
- testes de isolamento.

Saída: dois tenants sintéticos e prova automatizada de que não vazam dados.

## Incremento 3 — Primeiro vertical de incidente

- site + severity;
- `POST /incidents`;
- `GET /incidents`;
- `GET /incidents/{id}`;
- evento `INCIDENT_CREATED`;
- telas Angular para listar/criar/detalhar.

Saída: primeira demonstração ponta a ponta com persistência real.

## Incremento 4 — Operação do incidente

- acknowledge;
- update;
- protocol links;
- resolve;
- reopen;
- timeline;
- UI com status e feedback.

## Incremento 5 — Comunicação

- templates/versionamento;
- render alert/update/normalization;
- histórico do texto produzido;
- preview/copy, sem envio automático.

## Incremento 6 — Plantão

- configuração de turno/timezone;
- dashboard;
- envelhecimento/meta de atualização;
- handover preview;
- snapshot/finalize/version.

## Incremento 7 — Administração e auditoria

- RBAC completo;
- base operacional;
- memberships;
- audit events;
- export controlado.

## Incremento 8 — Cloud demo

- Docker final;
- IaC;
- Azure;
- observabilidade;
- CD;
- smoke tests;
- seed sintético.

## Ordem de decisão antes do primeiro commit de código

1. versão exata de Python/Node/Angular;
2. gerenciador de dependências Python;
3. ORM/migration stack;
4. estratégia de IDs (UUIDv7/ULID/UUID4);
5. library OIDC front/back;
6. Bicep vs Terraform;
7. convenção de commits/releases.

Essas escolhas operacionais devem virar ADR quando tiverem impacto duradouro.