# Sprint 002 — Incidentes & Timeline

**Status:** Concluída tecnicamente  
**Consolidação:** 2026-09-13  
**Release candidata:** `v0.2.0-alpha`  
**Sprint Goal:** completar o ciclo operacional ALERTA → ATUALIZAÇÃO → NORMALIZAÇÃO com timeline rastreável e mecanismos de priorização da lista.

## User Stories

### US-004 — Atualizar incidente [P0] — CONCLUÍDA
Como operador NOC, quero registrar atualizações em um incidente ativo para manter a operação informada sobre sua evolução.

Entregue:
- endpoint `POST /api/v1/incidents/{incident_id}/updates`;
- `message` validada e persistida como evento append-only;
- ator e timestamp derivados pelo backend;
- versão do incidente incrementada;
- atualização bloqueada após `RESOLVED/CLOSED`;
- UI de atualização preservando o contexto do detalhe.

### US-005 — Normalizar incidente [P0] — CONCLUÍDA
Como operador NOC, quero normalizar um incidente quando o serviço for restabelecido para registrar corretamente seu encerramento operacional.

Entregue:
- endpoint `POST /api/v1/incidents/{incident_id}/normalize`;
- transição para `RESOLVED`;
- observação opcional;
- evento append-only com ator/timestamp;
- segunda normalização bloqueada com `409`;
- confirmação explícita no frontend.

### US-006 — Visualizar timeline [P0] — CONCLUÍDA
Como operador NOC, quero visualizar a sequência cronológica de eventos para entender rapidamente o histórico do incidente.

Entregue:
- `GET /api/v1/incidents/{incident_id}/timeline`;
- eventos ordenados cronologicamente;
- tipos `INCIDENT_CREATED`, `INCIDENT_UPDATED` e `INCIDENT_NORMALIZED`;
- ator, data/hora e mensagem;
- estados de loading, erro e vazio no frontend;
- `incident_events` persistida de modo append-only no fluxo suportado.

### US-007 — Filtrar e ordenar incidentes [P1] — CONCLUÍDA
Como operador NOC, quero filtrar e ordenar incidentes para priorizar rapidamente os casos relevantes.

Entregue:
- `GET /api/v1/incidents/query`;
- filtros por status, severidade e período de início;
- `page` e `page_size` com limite de 1–100 itens;
- ordenação por `started_at` ou `updated_at`, `asc|desc`;
- resposta `{items, page, page_size, total}`;
- validação server-side de enum, limites e período;
- filtros, ordenação e navegação anterior/próxima no Angular;
- `GET /api/v1/incidents` legado preservado.

## Decisões de implementação

- O incidente representa o estado corrente; `IncidentEvent` registra a trilha operacional append-only.
- A normalização da Sprint 2 usa `RESOLVED`; `CLOSED` permanece estado previsto para evolução posterior.
- A consulta avançada foi adicionada em `/incidents/query` para preservar o contrato simples de `/incidents`.
- Tenant e ator permanecem autoridade server-side.
- A identidade demo continua restrita a `development/test`; OIDC/RBAC não fazem parte desta Sprint.

## Evidências

- PR #35 — backend de atualização, normalização e timeline; CI #50 (`34773862892`) verde após correção de ordenação de flush SQLAlchemy.
- PR #36 — frontend de atualização, confirmação de normalização e timeline; CI #52 (`34774195132`) verde.
- PR #37 — filtros, paginação e ordenação; CI #58 (`34775498607`) verde e Frontend Foundation #23 (`34775498603`) verde.
- Sprint 2 Functional Smoke #4 (`34775498602`) verde no head final do PR #37.
- Merge da US-007 na `main`: `805dde4239c162d21d3fe89644e396476633d319`.

## QA e regressão

Cobertura relevante:
- criar → atualizar → timeline → normalizar;
- timeline criada/atualizada/normalizada em ordem;
- segunda normalização → `409`;
- atualização pós-resolução → `409`;
- payloads de ação com campos de autoridade forjados → `422`;
- 404 para incidente/timeline inexistentes;
- filtros por status/severidade;
- paginação e total;
- ordenação por início/última atualização;
- parâmetros de query inválidos → `422`;
- período invertido bloqueado no frontend e backend;
- regressão da jornada Sprint 1 preservada.

## Segurança / AppSec

Para o escopo local/teste:
- consultas, detalhe, eventos e comandos usam tenant do contexto server-side;
- `tenant_id` e `actor_subject` não são autoridade do body;
- queries SQLAlchemy são parametrizadas;
- transições inválidas são verificadas no service;
- timeline não possui endpoint de edição/remoção;
- dependency audits continuam no CI;
- nenhuma credencial ou dado operacional real foi introduzido.

Não há autorização para exposição pública/produção enquanto identidade confiável e RBAC não forem implementados.

## Independent Code Review

Durante o fechamento foi identificado e corrigido um problema de manutenibilidade: a primeira versão da consulta avançada registrava a rota por efeito colateral de import. O código final registra o router explicitamente no app.

Classificação final para o escopo suportado:
- BLOCKER: 0 pendentes;
- MAJOR: 0 pendentes;
- Critical/High AppSec conhecido no escopo suportado: 0 aberto;
- sugestões futuras não bloqueiam a alpha local/teste.

## Definition of Done

- US-004/005/006/007 implementadas;
- migrations PostgreSQL válidas;
- backend lint/test/audit/readiness verdes;
- frontend type-check/test/build/audit verdes;
- compose regression smoke verde;
- Sprint 2 full-stack smoke verde;
- revisão independente sem BLOCKER/MAJOR pendente;
- documentação atualizada;
- candidata homologável apenas em local/teste.

## Release

Roteiro manual: [`../releases/V0.2.0-ALPHA-HOMOLOGATION.md`](../releases/V0.2.0-ALPHA-HOMOLOGATION.md).

Nenhuma tag, GitHub Release ou implantação Azure/produção é criada por este fechamento.
