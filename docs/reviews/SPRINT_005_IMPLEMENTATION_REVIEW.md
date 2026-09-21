# Sprint 005 — Implementation Review

**Data:** 2026-09-21  
**PR:** #59

## Objetivo

Revisar adversarialmente auditoria, correlação, logging, health e paridade do private demo antes do merge.

## Achados durante a implementação

### I1 — Lint Python

O primeiro CI detectou import duplicado em `app/main.py` e import não utilizado em teste.

**Correção:** imports corrigidos antes da rodada final.

### I2 — Paridade do Cloudflare private demo

A revisão encontrou que o Worker/D1 versionado ainda não possuía o contrato de Dashboard/Handover da Sprint 4, embora a UI já dependesse dele.

**Risco:** demo privada poderia ser descrita como full-stack sem paridade funcional do código canônico.

**Correção:** Worker recebeu Dashboard, preview/finalização/history/latest/by-id de handover, permissions correspondentes e schema D1 necessário.

### I3 — Auditoria ausente no adapter D1

A primeira implementação da Sprint 5 cobria PostgreSQL/FastAPI, mas a demo privada ficaria sem `/audit-events`.

**Correção:** D1 recebeu `audit_events`, auditoria atômica nas mutações suportadas, RBAC e consulta tenant-scoped.

### I4 — Liveness tocava D1

O Worker tratava live e ready pelo mesmo caminho e ambos inicializavam schema.

**Correção:** `/health/live` não toca datastore; `/health/ready` valida D1.

### I5 — Correlação do Worker

O Worker gerava sempre novo request ID e não propagava `X-Request-ID` válido.

**Correção:** validação/propagação equivalente ao backend canônico e log JSON allowlisted.

## Segurança

- nenhum body é copiado para audit trail;
- logging HTTP não inclui Authorization/Cookie;
- `audit:read` somente Admin/Supervisor;
- auditoria tenant-scoped;
- mutações e audit event usam a mesma transação/batch;
- nenhum endpoint de update/delete de audit event.

## Gate final

Merge somente após todos os checks do head final ficarem verdes, incluindo Sprint 5 Functional Smoke.
