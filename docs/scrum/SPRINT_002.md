# Sprint 002 — Incidentes & Timeline

**Status:** Planejamento futuro  
**Duração planejada:** 2 semanas  
**Release alvo:** `v0.2.0-alpha`  
**Sprint Goal:** completar o ciclo operacional ALERTA → ATUALIZAÇÃO → NORMALIZAÇÃO com timeline rastreável.

## User Stories

### US-004 — Atualizar incidente [P0]
Como operador NOC, quero registrar atualizações em um incidente ativo para manter a operação informada sobre sua evolução.

**Responsável primário:** 05 Backend & API  
**Dependências:** UX, domínio Incident, timeline, FE.

**Aceite:** atualização persistida; autor/data-hora registrados; incidente inexistente ou normalizado tratado; API documentada; UI atualizada sem perder contexto.

### US-005 — Normalizar incidente [P0]
Como operador NOC, quero normalizar um incidente quando o serviço for restabelecido para registrar corretamente seu encerramento operacional.

**Responsável primário:** 05 Backend & API

**Aceite:** transição válida; data/hora e autor; evento na timeline; dupla normalização impedida; confirmação UX para ação crítica.

### US-006 — Visualizar timeline [P0]
Como operador NOC, quero visualizar a sequência cronológica de eventos para entender rapidamente o histórico do incidente.

**Responsável primário:** 04 Frontend

**Aceite:** eventos ordenados; tipo/autor/data-hora; carregamento/erro/vazio; timeline append-only no backend.

### US-007 — Filtrar e ordenar incidentes [P1]
Como operador NOC, quero filtrar e ordenar incidentes para priorizar rapidamente os casos relevantes.

**Responsável primário:** 04 Frontend

**Aceite:** filtros por status/severidade/período; paginação; ordenação; parâmetros validados na API.

## Distribuição por especialistas

- **01 PO:** regras de transição, normalização e estados permitidos.
- **02 Architecture:** domínio de timeline/eventos e contratos.
- **03 UX/UI:** timeline, confirmações, severidade e feedback.
- **04 Frontend:** telas de atualização/normalização/timeline/filtros.
- **05 Backend:** endpoints, regras e services.
- **06 Database:** IncidentEvent/timeline, índices e constraints.
- **07 QA:** happy path e negativos de transição.
- **08 DevOps:** manter CI e ambiente reproduzível.
- **09 Security:** autorização por ação e proteção contra mass assignment/IDOR.
- **10 Docs:** OpenAPI, docs de domínio e Sprint.
- **11 Review:** review independente.
- **12 Release:** homologação `v0.2.0-alpha`.

## Tasks principais

- TASK-PO-S2-01 fechar state machine do incidente;
- TASK-ARC-S2-01 contrato IncidentEvent;
- TASK-UX-S2-01 fluxo atualização/normalização/timeline;
- TASK-DB-S2-01 tabela/event store append-only equivalente;
- TASK-BE-S2-01 POST updates;
- TASK-BE-S2-02 POST normalize;
- TASK-BE-S2-03 GET timeline;
- TASK-BE-S2-04 filtros/paginação/ordenação;
- TASK-FE-S2-01 atualização;
- TASK-FE-S2-02 normalização;
- TASK-FE-S2-03 timeline;
- TASK-FE-S2-04 filtros/paginação;
- TASK-QA-S2-01 fluxo criar→atualizar→normalizar;
- TASK-QA-S2-02 atualizar normalizado/normalizar duas vezes/404/payload inválido;
- TASK-SEC-S2-01 revisão de autorização e IDOR;
- TASK-DOC-S2-01 documentação;
- TASK-CR-S2-01 review;
- TASK-REL-S2-01 homologação.

## Dependências críticas

Sprint 1 homologada; state machine aprovada pelo PO; modelo de eventos aprovado por Architecture/Database.

## Critérios de sucesso

- ciclo completo executável pela UI;
- timeline consistente e append-only;
- transições inválidas bloqueadas;
- filtros/paginação funcionais;
- testes/regressão verdes;
- sem BLOCKER ou vulnerabilidade Critical/High sem mitigação;
- release homologada.
