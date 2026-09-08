# Sprint 004 — Dashboard & Passagem de Turno

**Status:** Planejamento futuro  
**Duração planejada:** 2 semanas  
**Release alvo:** `v0.4.0-beta`  
**Sprint Goal:** permitir continuidade operacional entre turnos com visão rápida dos incidentes e pendências.

## User Stories

### US-011 — Dashboard operacional [P0]
Como operador NOC, quero visualizar rapidamente incidentes ativos, críticos e pendências para priorizar minha atuação.

**Responsável primário:** 04 Frontend

### US-012 — Criar passagem de turno [P0]
Como operador que encerra o turno, quero registrar uma passagem estruturada para transferir contexto e próximos passos ao operador seguinte.

**Responsável primário:** 05 Backend & API

### US-013 — Consultar passagem de turno [P0]
Como operador que inicia o turno, quero consultar a passagem anterior para assumir a operação sem perder contexto.

**Responsável primário:** 04 Frontend

## Conteúdo mínimo do handover

Incidentes ativos, pendências, protocolos, próximo passo, observações, responsável e timestamps.

## Distribuição por especialistas

- **01 PO:** regra e conteúdo obrigatório do handover.
- **02 Architecture:** boundaries entre Incident e Shift/Handover.
- **03 UX/UI:** dashboard de baixa carga cognitiva e fluxo de passagem.
- **04 Frontend:** dashboard, criação/consulta da passagem.
- **05 Backend:** APIs e regras de handover.
- **06 Database:** Shift, ShiftHandover e itens relacionados.
- **07 QA:** cenários sem incidentes, múltiplos incidentes e concorrência/contexto.
- **08 DevOps:** CI e observabilidade básica do novo fluxo.
- **09 Security:** autorização e tenant isolation.
- **10 Docs:** domínio, API, UX e Sprint.
- **11 Review:** review independente.
- **12 Release:** homologação `v0.4.0-beta`.

## Tasks principais

TASK-PO-S4-01 regras de handover; TASK-ARC-S4-01 modelo de domínio; TASK-UX-S4-01 dashboard; TASK-UX-S4-02 passagem; TASK-DB-S4-01 schema; TASK-BE-S4-01 criar handover; TASK-BE-S4-02 consultar handovers; TASK-FE-S4-01 dashboard; TASK-FE-S4-02 editor; TASK-FE-S4-03 consulta; TASK-QA-S4-01 fluxo de passagem; TASK-SEC-S4-01 autorização/tenant; TASK-DOC-S4-01 docs; TASK-CR-S4-01 review; TASK-REL-S4-01 homologação.

## Critérios de sucesso

- operador identifica rapidamente situação atual;
- passagem pode ser criada e consultada;
- histórico preserva autoria e timestamps;
- isolamento por tenant permanece válido;
- testes críticos verdes;
- release homologada.
