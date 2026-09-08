# Sprint 001 — Work Packages por Especialista

**Projeto:** P0 — NOC Flow Cloud v2  
**Sprint:** 001 — Fundação Executável  
**Objetivo:** entregar uma base executável Angular + FastAPI + PostgreSQL, com primeiro vertical slice de incidentes, testes, Docker, CI e quality gates.

## Ordem de despacho

01 Product Owner → 02 Architecture → 03 UX / 06 Database / 09 Security → 05 Backend / 04 Frontend → 08 DevOps → 07 QA → 11 Code Review → 10 Documentation → 12 Release.

---

## 01 — Product Owner & Backlog

**Card Trello:** EN-006 — Product Scope & Sprint Readiness

### Tarefas
- TASK-PO-001 — definir campos, regras e validações mínimas de criação de incidente;
- TASK-PO-002 — validar US-001, US-002 e US-003 contra MVP e Definition of Ready;
- TASK-PO-003 — confirmar escopo excluído da Sprint 1 e registrar dependências funcionais.

### Entregáveis
- regras funcionais consolidadas;
- critérios de aceite objetivos;
- histórias classificadas como READY ou NOT READY.

### Gate de saída
Nenhuma ambiguidade funcional crítica pendente para US-001/002/003.

---

## 02 — Software Architecture

**Card Trello:** EN-001 — Arquitetura baseline

### Tarefas
- TASK-ARC-001 — fechar arquitetura Angular/FastAPI e estrutura modular;
- TASK-ARC-002 — definir /api/v1, padrão de erros e boundaries;
- TASK-ARC-003 — definir tenant_id, configuração, logging e ADRs obrigatórios.

### Entregáveis
- arquitetura baseline aprovada;
- ADRs necessários;
- contratos suficientes para FE/BE/DB/DevOps iniciarem.

### Gate de saída
Nenhuma decisão estrutural P0 bloqueando implementação.

---

## 03 — UX/UI Design

**Card Trello:** EN-007 — UX Foundation

### Tarefas
- TASK-UX-001 — fluxo Lista → Criar → Detalhe;
- TASK-UX-002 — formulário e prevenção de erro;
- TASK-UX-003 — loading/empty/error/success, responsividade e acessibilidade.

### Entregáveis
- fluxo e wireframe de baixa/média fidelidade;
- especificação de estados e validações;
- regras de interação para Frontend.

### Gate de saída
Frontend consegue implementar US-001/002/003 sem decisão UX crítica em aberto.

---

## 04 — Frontend

**Card Trello:** EN-004 — Frontend Foundation

### Tarefas
- TASK-FE-001 — bootstrap Angular, routing, shell e environments;
- TASK-FE-002 — HttpClient, API service, loading e error handling;
- TASK-FE-003 — lista e detalhe via API real;
- TASK-FE-004 — formulário de criação e feedback de sucesso/erro.

### Entregáveis
- aplicação Angular executável;
- rotas de lista/criação/detalhe;
- integração real com FastAPI;
- estados UX implementados.

### Gate de saída
US-001/002/003 funcionalmente demonstráveis no frontend.

---

## 05 — Backend & API

**Card Trello:** EN-003 — Backend Foundation

### Tarefas
- TASK-BE-001 — bootstrap FastAPI, settings, DI, /api/v1 e exceptions;
- TASK-BE-002 — SQLAlchemy/PostgreSQL e healthcheck;
- TASK-BE-003 — POST /api/v1/incidents;
- TASK-BE-004 — GET /api/v1/incidents e GET /api/v1/incidents/{id}.

### Entregáveis
- API executável;
- OpenAPI coerente;
- validação e persistência;
- respostas de erro padronizadas.

### Gate de saída
Fluxo criar/listar/detalhar validável por API sem lógica de negócio nas routes.

---

## 06 — Database & Data Model

**Card Trello:** EN-002 — Database Foundation

### Tarefas
- TASK-DB-001 — Tenant e Incident com tenant_id/timestamps;
- TASK-DB-002 — PK/FK/constraints/índices;
- TASK-DB-003 — migration inicial PostgreSQL.

### Entregáveis
- schema inicial;
- migrations reproduzíveis;
- integridade e índices mínimos documentados.

### Gate de saída
Banco pode ser criado do zero por migration e suporta o vertical slice da Sprint.

---

## 07 — QA & Automated Tests

**Card Trello:** EN-009 — QA Strategy & Sprint 1 Tests

### Tarefas
- TASK-QA-001 — testes API criar/listar/detalhar;
- TASK-QA-002 — testes negativos: payload inválido, 404 e persistência;
- TASK-QA-003 — testes frontend de estados e formulário;
- TASK-QA-004 — smoke FE+BE+DB via Docker.

### Entregáveis
- cenários derivados dos critérios de aceite;
- suíte crítica automatizada;
- evidências de smoke e bugs.

### Gate de saída
Critérios P0 testáveis e suíte crítica verde.

---

## 08 — DevOps, Azure & CI/CD

**Card Trello:** EN-005 — Docker + CI

### Tarefas
- TASK-DO-001 — Dockerfiles frontend/backend + PostgreSQL;
- TASK-DO-002 — docker-compose FE+BE+DB;
- TASK-DO-003 — GitHub Actions lint → tests → build → security checks.

### Entregáveis
- ambiente local reproduzível;
- pipeline inicial;
- configuração sem secrets versionados.

### Gate de saída
`docker compose up` sobe a stack e CI passa em PR.

---

## 09 — Security & AppSec

**Card Trello:** EN-008 — Security Baseline

### Tarefas
- TASK-SEC-001 — threat model inicial;
- TASK-SEC-002 — CORS, secrets/.env, configuração segura e logs;
- TASK-SEC-003 — OWASP API e riscos de tenant isolation.

### Entregáveis
- relatório de riscos;
- mitigação prática para Critical/High;
- recomendações para arquitetura e implementação.

### Gate de saída
Nenhum Critical/High conhecido sem mitigação definida.

---

## 10 — Documentation & Portfolio

**Card Trello:** EN-010 — Sprint 1 Documentation

### Tarefas
- TASK-DOC-001 — README/setup e pré-requisitos;
- TASK-DOC-002 — SPRINT_001.md + API/Architecture/Security impactados;
- TASK-DOC-003 — evidências: PRs, testes, screenshots, decisões e release notes.

### Entregáveis
- documentação sincronizada com o estado real;
- evidências de portfólio da Sprint.

### Gate de saída
Um terceiro consegue clonar, executar e entender o que foi entregue.

---

## 11 — Code Review & Refactoring

**Card Trello:** EN-011 — Independent Code Review

### Tarefas
- TASK-CR-001 — revisar frontend, backend e migrations;
- TASK-CR-002 — verificar arquitetura, segurança, testabilidade, duplicação e complexidade;
- TASK-CR-003 — registrar BLOCKER/MAJOR/MINOR/SUGGESTION e impedir homologação com BLOCKER aberto.

### Entregáveis
- parecer independente;
- lista de findings e recomendações.

### Gate de saída
Nenhum BLOCKER pendente.

---

## 12 — Releases & Homologation

**Card Trello:** EN-012 — Homologação v0.1.0-alpha

### Tarefas
- TASK-REL-001 — validar build, CI, migrations, testes e security checks;
- TASK-REL-002 — smoke criar → listar → detalhar;
- TASK-REL-003 — emitir decisão formal de homologação.

### Entregáveis
- evidências de homologação;
- decisão REPROVADA / APROVADA COM RESSALVAS / APROVADA;
- blockers devolvidos ao responsável.

### Gate de saída
Release `v0.1.0-alpha` classificada formalmente.

---

## Definition of Done aplicada à Sprint

Um item só é DONE quando: implementação concluída; critérios de aceite atendidos; testes relevantes aprovados; CI verde; sem BLOCKER de review; sem Critical/High de segurança sem tratamento; documentação impactada atualizada; evidências registradas.

## Regra de coordenação

O Scrum Master/Orchestrator não altera unilateralmente escopo, contratos de API, arquitetura ou modelo de dados. Impedimentos retornam ao chat especialista responsável e mudanças de escopo retornam ao Product Owner.