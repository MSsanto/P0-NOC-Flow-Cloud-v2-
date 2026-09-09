# Sprint 1 — Fundação Executável

> Resumo executivo e evidências de execução. O contrato completo da Sprint permanece em [`../scrum/SPRINT_001.md`](../scrum/SPRINT_001.md).

**Data de consolidação:** 2026-09-09  
**Release candidata:** `v0.1.0-alpha`  
**Sprint Goal:** base executável, testável e reproduzível com Angular, FastAPI, PostgreSQL e primeiro vertical slice de incidentes.

## Entregas

- US-001 — Listar incidentes: backend + frontend implementados.
- US-002 — Criar incidente: backend + frontend implementados.
- US-003 — Visualizar detalhe: backend + frontend implementados.
- EN-001 — Arquitetura baseline: concluída.
- EN-002 — Database foundation: concluída e validada com PostgreSQL real.
- EN-003 — Backend foundation: concluída.
- EN-004 — Frontend foundation: concluída.
- EN-005 — Docker Compose + CI: concluída.
- EN-006 — Escopo MVP: concluído.
- EN-007 — UX foundation: concluída.
- EN-008 — Security baseline: revisão final em PR dedicado.
- EN-009 — QA: smoke funcional full-stack em PR dedicado.
- EN-010 — Documentação/setup: este fechamento documental.
- EN-011 — Code Review independente: gate anterior à homologação.
- EN-012 — Homologação: gate final da Sprint.

## Evidências principais

| Evidência | Resultado |
|---|---|
| PR #19 / CI run `34380340323` | PostgreSQL 17, Alembic, Ruff, pytest, pip-audit e readiness verdes |
| PR #9 / Frontend run `34381183509` | npm ci, type-check, testes e build Angular verdes |
| PR #24 / CI run `34390935250` | Docker Compose FE+BE+DB e smoke HTTP verdes |
| PR #16 / CI run `34391528258` | 17 testes backend, integração HTTP/PostgreSQL, audits e Compose verdes |
| PR #25 / CI run `34392059532` | frontend funcional: type-check, 5 testes, build, audits e Compose verdes |

## Fluxo executável

```text
Angular/Nginx
    ↓ /api/v1
FastAPI
    ↓ SQLAlchemy
PostgreSQL 17
```

Jornada entregue:

```text
Lista de incidentes → Novo incidente → Detalhe do incidente
```

## Defeitos encontrados durante a Sprint

1. descoberta de pacotes Python incluía `alembic` como top-level package;
2. imports Alembic fora da ordem Ruff;
3. Vitest 3 incompatível com Angular Build 22;
4. npm 10.9.8 falhava ao gerar lockfile (`edgesOut`);
5. opções TypeScript 6 obsoletas (`baseUrl`/`downlevelIteration`);
6. tipagem de teste incompatível com Vitest 4;
7. `tests/conftest.py` anulava PostgreSQL do CI com SQLite;
8. teste frontend assumia base URL relativa apesar do environment de development;
9. compose-smoke executava antes de a infraestrutura Docker existir.

Todos foram corrigidos e cobertos pelos gates atuais.

## Limites conhecidos

- identidade real/OIDC e autorização não fazem parte da Sprint 1;
- provider demo só é suportado em `development`/`test`;
- nenhuma autorização de deploy público/produção foi concedida;
- credenciais padrão do Compose são apenas locais;
- timeline, edição, normalização, handover e dashboard pertencem às próximas Sprints.

## Gate para homologação

A candidata `v0.1.0-alpha` só pode ser aprovada após:

- CI completo verde;
- smoke funcional criar/listar/detalhar verde;
- EN-008 sem Critical/High não mitigado no escopo alpha;
- EN-011 sem BLOCKER;
- documentação alinhada ao comportamento atual.
