# Sprint 001 — Fundação Executável

**Status:** Planejamento ativo  
**Duração planejada:** 2 semanas  
**Release alvo:** `v0.1.0-alpha`  
**Sprint Goal:** entregar uma base executável, testável e reproduzível com Angular, FastAPI e PostgreSQL, incluindo o primeiro vertical slice de incidentes.

## User Stories

### US-001 — Listar incidentes [P0]
**Responsável primário:** 04 Frontend  
**Dependências:** EN-001, EN-002, EN-003, EN-004

Como operador NOC, quero visualizar os incidentes registrados para identificar rapidamente o estado atual da operação.

**Aceite:**
- lista consumida de API real;
- exibir ID, status, severidade e data/hora;
- loading, empty e error states;
- sem dados mock no caminho principal.

### US-002 — Criar incidente [P0]
**Responsável primário:** 05 Backend  
**Dependências:** US-001, UX, modelo Incident, API

Como operador NOC, quero registrar um novo incidente para documentar formalmente uma indisponibilidade ou degradação.

**Aceite:**
- campos obrigatórios definidos;
- validação frontend/backend;
- persistência PostgreSQL;
- ID e timestamp automáticos;
- tenant associado;
- payload inválido não gera registro parcial.

### US-003 — Visualizar detalhe [P0]
**Responsável primário:** 04 Frontend  
**Dependências:** US-001, US-002

Como operador NOC, quero abrir os detalhes de um incidente para analisar todas as informações registradas.

**Aceite:**
- rota por ID;
- consulta via API;
- tratamento de ID inexistente;
- refresh preserva rota/contexto;
- dados completos da versão inicial exibidos.

## Enablers e distribuição por chat

| ID | Entrega | Responsável |
|---|---|---|
| EN-001 | Arquitetura baseline + ADRs | 02 Software Architecture |
| EN-002 | Database foundation + migrations | 06 Database & Data Model |
| EN-003 | Backend FastAPI foundation | 05 Backend & API |
| EN-004 | Frontend Angular foundation | 04 Frontend |
| EN-005 | Docker Compose + CI inicial | 08 DevOps, Azure & CI/CD |
| EN-006 | Escopo MVP e critérios funcionais | 01 Product Owner & Backlog |
| EN-007 | UX foundation do fluxo de incidentes | 03 UX/UI Design |
| EN-008 | Threat model e security baseline | 09 Security & AppSec |
| EN-009 | Estratégia e suíte de testes S1 | 07 QA & Automated Tests |
| EN-010 | Documentação da Sprint e setup | 10 Documentation & Portfolio |
| EN-011 | Code Review independente | 11 Code Review & Refactoring |
| EN-012 | Homologação da `v0.1.0-alpha` | 12 Releases & Homologation |

## Task Breakdown

### 01 Product Owner
- TASK-PO-001 definir campos/regras mínimas de criação de incidente;
- TASK-PO-002 validar US-001/002/003 e critérios de aceite;
- TASK-PO-003 confirmar escopo fora da Sprint.

### 02 Architecture
- TASK-ARC-001 arquitetura Angular;
- TASK-ARC-002 arquitetura FastAPI;
- TASK-ARC-003 modular monolith;
- TASK-ARC-004 `/api/v1`;
- TASK-ARC-005 error handling;
- TASK-ARC-006 estratégia multi-tenant;
- TASK-ARC-007 ADRs essenciais.

### 03 UX/UI
- TASK-UX-001 fluxo lista → criar → detalhe;
- TASK-UX-002 formulário e validações;
- TASK-UX-003 loading/empty/error/success;
- TASK-UX-004 especificação responsiva e acessível.

### 04 Frontend
- TASK-FE-001 listagem de incidentes;
- TASK-FE-002 estados da listagem;
- TASK-FE-003 integração GET incidents;
- TASK-FE-004 formulário;
- TASK-FE-005 validações;
- TASK-FE-006 integração POST incident;
- TASK-FE-007 rota detalhe;
- TASK-FE-008 tela detalhe;
- TASK-FE-009..014 bootstrap, routing, shell, environment, HttpClient e error handling.

### 05 Backend
- TASK-BE-001 endpoint de listagem;
- TASK-BE-002 service/repository de consulta;
- TASK-BE-003 schema de criação;
- TASK-BE-004 service de criação;
- TASK-BE-005 persistência;
- TASK-BE-006 endpoint de detalhe;
- TASK-BE-007..013 bootstrap, settings, SQLAlchemy, DI, exceptions, health e OpenAPI.

### 06 Database
- TASK-DB-001 suporte à listagem;
- TASK-DB-002 persistência de Incident;
- TASK-DB-003 PostgreSQL local;
- TASK-DB-004 migrations;
- TASK-DB-005 Tenant;
- TASK-DB-006 Incident;
- TASK-DB-007 constraints;
- TASK-DB-008 índices essenciais.

### 07 QA
- TASK-QA-001 testes API listagem;
- TASK-QA-002 testes frontend listagem;
- TASK-QA-003 criação válida;
- TASK-QA-004 criação inválida/negativa;
- TASK-QA-005 detalhe/404;
- TASK-QA-006 smoke test FE+BE+DB.

### 08 DevOps
- TASK-DO-001 Dockerfile frontend;
- TASK-DO-002 Dockerfile backend;
- TASK-DO-003 serviço PostgreSQL;
- TASK-DO-004 docker-compose;
- TASK-DO-005 GitHub Actions: lint → tests → build → security checks.

### 09 Security
- TASK-SEC-001 threat model inicial;
- TASK-SEC-002 CORS e configuração segura;
- TASK-SEC-003 secrets e `.env`;
- TASK-SEC-004 riscos de tenant isolation;
- TASK-SEC-005 revisão OWASP API do vertical slice.

### 10 Documentation
- TASK-DOC-001 atualizar README/setup;
- TASK-DOC-002 manter Sprint 001;
- TASK-DOC-003 atualizar API/Architecture/Security impactados;
- TASK-DOC-004 registrar evidências para portfólio.

### 11 Code Review
- TASK-CR-001 revisar FE;
- TASK-CR-002 revisar BE;
- TASK-CR-003 revisar migrations/DB;
- TASK-CR-004 classificar BLOCKER/MAJOR/MINOR/SUGGESTION.

### 12 Release
- TASK-REL-001 validar build e CI;
- TASK-REL-002 smoke da jornada criar/listar/detalhar;
- TASK-REL-003 validar testes/security/docs;
- TASK-REL-004 emitir decisão de homologação.

## Dependências críticas

`01 PO → 02 Architecture → 03 UX / 06 DB / 09 Security → 05 Backend + 04 Frontend → 08 DevOps → 07 QA → 11 Review → 10 Docs → 12 Release`

## Definition of Ready aplicada

Uma história só entra em execução quando objetivo, aceite, dependências, contrato necessário e decisão arquitetural relevante estiverem definidos.

## Critérios de sucesso da Sprint

- `docker compose` sobe frontend, backend e banco;
- healthcheck funcional;
- criar/listar/detalhar incidente funciona ponta a ponta;
- CI verde;
- testes críticos aprovados;
- nenhum BLOCKER de review ou Critical/High sem mitigação;
- documentação reflete o estado real;
- homologação registrada.

## Evidências / Review / Retro

A preencher durante e ao final da Sprint: PRs, builds, testes, security checks, demo, bugs, feedback, itens concluídos/não concluídos e ações de retrospectiva.
