# Sprint 1 — Fundação Executável

> Resumo executivo e evidências de execução. O contrato detalhado permanece em [`../scrum/SPRINT_001.md`](../scrum/SPRINT_001.md).

**Consolidação:** 2026-09-10  
**Release candidata:** `v0.1.0-alpha`  
**Sprint Goal:** entregar uma base executável, testável e reproduzível com Angular, FastAPI, PostgreSQL e o primeiro vertical slice de incidentes.

## Entregas

### User Stories

- US-001 — Listar incidentes: concluída e validada ponta a ponta.
- US-002 — Criar incidente: concluída e validada, incluindo casos negativos.
- US-003 — Visualizar detalhe: concluída e validada ponta a ponta.

### Enablers

- EN-001 — Arquitetura baseline: concluída.
- EN-002 — Database Foundation: concluída com PostgreSQL/Alembic.
- EN-003 — Backend Foundation: concluída.
- EN-004 — Frontend Foundation: concluída.
- EN-005 — Docker + CI: concluída.
- EN-006 — Product Scope & Sprint Readiness: concluída.
- EN-007 — UX Foundation: concluída.
- EN-008 — Security Baseline: concluída para alpha local/teste.
- EN-009 — QA Strategy & Sprint 1 Tests: concluída.
- EN-010 — Documentação: fechamento final desta Sprint.
- EN-011 — Independent Code Review: concluída, com MAJOR corrigido.
- EN-012 — Homologação: executada após o merge desta documentação e CI final da `main`.

## Fluxo executável

```text
Angular / Nginx
      ↓ /api/v1
    FastAPI
      ↓ SQLAlchemy
 PostgreSQL 17
```

Jornada funcional:

```text
Lista de incidentes → Registrar incidente → Detalhe do incidente
```

## Evidências principais

| Evidência | Resultado |
|---|---|
| PR #11 | arquitetura baseline consolidada |
| PR #14 | contrato US-002 e gate documental consolidados |
| PR #19 / run `34380340323` | PostgreSQL 17, Alembic, Ruff, pytest, pip-audit e readiness verdes |
| PR #9 / run `34381183509` | Angular: install, type-check, testes e build verdes |
| PR #24 / run `34390935250` | Docker Compose FE+BE+DB e smoke HTTP verdes |
| PR #16 / run `34391528258` | 17 testes backend + integração PostgreSQL + audits + Compose |
| PR #25 / run `34392059532` | telas US-001/002/003 + testes/build/audits |
| PR #26 / run `34392403933` | smoke funcional Nginx → FastAPI → PostgreSQL: criar/listar/detalhar + 422 |
| PR #27 / run `34392517493` | baseline AppSec + headers + audits + Compose |
| PR #29 / run `34528173526` | correção do MAJOR de review + regressão completa verde |

## Defeitos encontrados e corrigidos

Durante a execução, os gates encontraram problemas reais que foram corrigidos antes do fechamento:

1. descoberta de pacotes Python incluía `alembic` como pacote top-level;
2. imports Alembic incompatíveis com Ruff;
3. incompatibilidade Vitest/Angular Build;
4. falha do npm 10 ao gerar lockfile no cenário usado;
5. opções TypeScript obsoletas;
6. tipagem de teste incompatível com Vitest 4;
7. `tests/conftest.py` anulava PostgreSQL do CI com SQLite;
8. teste frontend assumia URL relativa enquanto development usa origem absoluta;
9. compose-smoke disparava antes da infraestrutura Docker existir;
10. formulário frontend não espelhava `trim()` e a regra de `started_at` futuro do backend;
11. teste de `datetime-local` dependia do timezone do runner CI.

Os itens foram corrigidos e revalidados antes de avançar os respectivos gates.

## Code Review independente

Classificação final:

- **BLOCKER:** 0 pendentes;
- **MAJOR:** 1 encontrado e corrigido no PR #29;
- **MINOR:** nenhum impeditivo para a alpha;
- **SUGGESTION:** melhorias futuras não bloqueiam o escopo da Sprint 1.

O MAJOR dizia respeito à consistência de validação frontend/backend. O frontend passou a validar comprimento útil após `trim()`, impedir data/hora futura e normalizar as strings antes do POST.

## Segurança

Para o escopo da alpha local/teste:

- tenant scoping é imposto server-side;
- `tenant_id`/ator não são aceitos como autoridade do body;
- validação Pydantic e constraints de banco estão presentes;
- queries usam SQLAlchemy parametrizado;
- CORS é allowlist;
- erros usam Problem Details sem exposição de stack/SQL/secrets;
- backend container executa como usuário não-root;
- Nginx possui headers de segurança;
- `pip-audit` e `npm audit` fazem parte do gate CI.

**Produção não está liberada.** OIDC/RBAC e identidade confiável pertencem ao incremento planejado e substituem o provider demo antes de exposição pública.

## Definition of Done — evidência técnica

- requisitos/aceite: atendidos para US-001/002/003;
- migrations: executadas contra PostgreSQL real;
- backend tests: verdes;
- frontend tests/type-check/build: verdes;
- dependency audits: verdes;
- Docker Compose: verde;
- smoke funcional: verde;
- AppSec: sem Critical/High aberto no escopo suportado;
- independent code review: sem BLOCKER/MAJOR pendente;
- documentação: atualizada neste fechamento;
- deploy público/produção: não faz parte desta release alpha.

## Homologação

O roteiro reproduzível está em [`../releases/V0.1.0-ALPHA-HOMOLOGATION.md`](../releases/V0.1.0-ALPHA-HOMOLOGATION.md).

A decisão formal deve considerar a `v0.1.0-alpha` como **alpha local/teste**, nunca como aprovação para produção.
