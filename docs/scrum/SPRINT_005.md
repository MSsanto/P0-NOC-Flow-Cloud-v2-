# Sprint 005 — Auditoria & Observabilidade

**Status:** Planejamento futuro  
**Duração planejada:** 2 semanas  
**Release alvo:** `v0.5.0-rc1`  
**Sprint Goal:** tornar o sistema rastreável, observável e resiliente antes da publicação estável.

## User Story

### US-014 — Consultar trilha de auditoria [P1]
Como administrador/supervisor, quero consultar ações relevantes para investigar alterações e reconstruir eventos operacionais.

**Responsável primário:** 05 Backend & API

**Aceite:** registrar ator, tenant, ação, entidade, ID e timestamp; acesso restrito; dados sensíveis não são expostos desnecessariamente.

## Enablers

- EN-S5-01 structured logging e correlation ID;
- EN-S5-02 `/health/live` e `/health/ready`;
- EN-S5-03 Application Insights/observabilidade equivalente;
- EN-S5-04 resiliência e tratamento de indisponibilidade;
- EN-S5-05 performance e revisão de índices;
- EN-S5-06 rodada formal de AppSec.

## Distribuição por especialistas

- **01 PO:** eventos de auditoria necessários e política de acesso.
- **02 Architecture:** padrão de observabilidade/correlation e audit boundaries.
- **03 UX/UI:** estados degradados e feedback de indisponibilidade.
- **04 Frontend:** tratamento de falhas e visualização autorizada da auditoria quando prevista.
- **05 Backend:** audit trail, logging e health endpoints.
- **06 Database:** audit schema/índices/performance.
- **07 QA:** resiliência, performance básica e regressão.
- **08 DevOps:** logs, métricas, Application Insights e alertas básicos.
- **09 Security:** OWASP Top 10/API, secrets, logs, dependencies e RBAC.
- **10 Docs:** observabilidade, troubleshooting e security docs.
- **11 Review:** review independente.
- **12 Release:** homologação `v0.5.0-rc1`.

## Tasks principais

TASK-ARC-S5-01 padrão de observabilidade; TASK-BE-S5-01 audit trail; TASK-BE-S5-02 correlation ID; TASK-BE-S5-03 health live/ready; TASK-DB-S5-01 audit/index review; TASK-FE-S5-01 degraded/error states; TASK-DO-S5-01 Application Insights; TASK-QA-S5-01 failure scenarios; TASK-QA-S5-02 performance; TASK-SEC-S5-01 AppSec formal; TASK-DOC-S5-01 runbook/troubleshooting; TASK-CR-S5-01 review; TASK-REL-S5-01 homologação.

## Critérios de sucesso

- ações críticas rastreáveis;
- logs estruturados sem secrets/tokens;
- requests correlacionáveis;
- readiness/liveness funcionais;
- falhas de dependências tratadas;
- rodada AppSec sem Critical/High aberto sem mitigação;
- release candidate homologada.
