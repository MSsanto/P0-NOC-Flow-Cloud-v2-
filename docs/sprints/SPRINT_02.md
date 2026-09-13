# Sprint 2 — Incidentes & Timeline

> Resumo executivo e evidências. O contrato detalhado está em [`../scrum/SPRINT_002.md`](../scrum/SPRINT_002.md).

**Consolidação:** 2026-09-13  
**Release candidata:** `v0.2.0-alpha`  
**Status:** concluída tecnicamente para ambiente local/teste.

## Entregas

- **US-004:** atualização operacional de incidente ativo.
- **US-005:** normalização com transição para `RESOLVED` e proteção contra repetição.
- **US-006:** timeline cronológica append-only com ator, horário, tipo e mensagem.
- **US-007:** filtros por status/severidade/período, paginação e ordenação.

## Jornada entregue

```text
Criar incidente
   ↓
Registrar atualização
   ↓
Visualizar timeline
   ↓
Filtrar / priorizar
   ↓
Normalizar incidente
   ↓
Timeline final + bloqueio de ações inválidas
```

## Evidências de CI

| Evidência | Resultado |
|---|---|
| PR #35 / CI #50 `34773862892` | backend update/normalize/timeline + migration/eventos verde |
| PR #36 / CI #52 `34774195132` | frontend update/normalização/timeline verde |
| PR #37 / CI #58 `34775498607` | backend/frontend/audits/regressão Compose verdes |
| Frontend Foundation #23 `34775498603` | type-check/test/build verde |
| Sprint 2 Functional Smoke #4 `34775498602` | ciclo Sprint 2 completo no stack Docker verde |

## Defeitos encontrados e corrigidos

1. SQLAlchemy podia tentar inserir o primeiro evento antes do incidente pai; corrigido com `flush()` do incidente antes do evento mantendo a mesma transação.
2. Registro inicial da rota de consulta avançada usava efeito colateral de import; substituído por registro explícito do router no app antes do merge.

## Contratos implementados

```text
POST /api/v1/incidents/{id}/updates
POST /api/v1/incidents/{id}/normalize
GET  /api/v1/incidents/{id}/timeline
GET  /api/v1/incidents/query
```

A listagem simples `GET /api/v1/incidents` foi preservada para retrocompatibilidade.

## Segurança

- tenant e ator continuam resolvidos server-side;
- payload não pode assumir campos de autoridade;
- recursos/eventos são tenant-scoped;
- conflitos de lifecycle retornam `409`;
- parâmetros inválidos retornam `422`;
- timeline não expõe endpoint de alteração/remoção;
- audits de dependência permanecem gates de CI.

## Decisão de homologação técnica

**APROVADA — ESCOPO LOCAL/TESTE.**

A aprovação não autoriza exposição pública, produção ou Azure. OIDC/RBAC e identidade confiável ainda são requisitos antes desse passo.

Roteiro manual: [`../releases/V0.2.0-ALPHA-HOMOLOGATION.md`](../releases/V0.2.0-ALPHA-HOMOLOGATION.md).
