# Roadmap — P0 NOC Flow Cloud v2

**Status:** baseline aprovado para planejamento  
**Modelo:** 6 Sprints de 2 semanas  
**Objetivo de release:** v1.0.0 ao final da Sprint 6

> O roadmap define a sequência de execução. Mudanças de escopo ou prioridade devem passar pelo Product Owner e ser coordenadas pelo Scrum Master/Orchestrator.

## Sprint 1 — Fundação Executável

**Release alvo:** `v0.1.0-alpha`

Objetivo: entregar Angular + FastAPI + PostgreSQL executáveis, Docker/CI inicial e o primeiro vertical slice de incidentes.

Principais entregas:
- arquitetura baseline e ADRs essenciais;
- UX inicial do fluxo de incidentes;
- modelo de dados inicial e migrations;
- security baseline;
- fundação FastAPI e Angular;
- criar, listar e detalhar incidente;
- Docker Compose e CI inicial;
- testes, code review, documentação e homologação.

## Sprint 2 — Incidentes & Timeline

**Release alvo:** `v0.2.0-alpha`

Objetivo: completar o ciclo operacional de incidente.

Principais entregas:
- atualização de incidente;
- normalização;
- timeline append-only;
- validação de transições;
- paginação, filtros e ordenação;
- estados UX de alerta, atualização e normalização;
- testes negativos e de regressão.

## Sprint 3 — Auth, RBAC & Multi-Tenancy

**Release alvo:** `v0.3.0-beta`

Objetivo: estabelecer identidade, autorização e isolamento seguro entre operações.

Principais entregas:
- OIDC/OAuth2 com Microsoft Entra ID ou abstração aprovada;
- roles Admin, Supervisor, Operator e Viewer;
- autorização server-side;
- tenant context seguro;
- isolamento por `tenant_id`;
- testes cross-tenant e de broken access control.

## Sprint 4 — Dashboard & Passagem de Turno

**Release alvo:** `v0.4.0-beta`

Objetivo: suportar continuidade operacional entre turnos NOC.

Principais entregas:
- dashboard operacional;
- incidentes críticos/ativos e pendências;
- Shift Handover;
- itens de passagem e próximos passos;
- histórico de passagens;
- filtros operacionais;
- testes do fluxo de handover.

## Sprint 5 — Auditoria & Observabilidade

**Release alvo:** `v0.5.0-rc1`

Objetivo: tornar a aplicação rastreável, observável e resiliente.

Principais entregas:
- audit trail;
- structured logging;
- correlation ID;
- health live/ready;
- Application Insights ou solução equivalente aprovada;
- testes de indisponibilidade e resiliência;
- revisão de índices/performance;
- rodada formal de AppSec.

## Sprint 6 — Azure & Release v1.0

**Release alvo:** `v1.0.0`

Objetivo: publicar, endurecer e homologar a primeira versão estável do projeto.

Principais entregas:
- ambientes development/test/staging/production;
- deploy Azure;
- pipeline final com gates;
- smoke/regression/E2E;
- hardening final;
- documentação de deployment/runbook/rollback;
- documentação de portfólio e screenshots;
- homologação final.

## Qualidade transversal

Em todas as Sprints:
- QA participa desde o refinamento;
- Security revisa mudanças relevantes;
- código passa por Code Review independente;
- documentação impactada é atualizada;
- Release/Homologation executa o quality gate;
- itens Done devem atender à [Definition of Done](DEFINITION_OF_DONE.md).

## Pós-v1.0

Ficam fora do MVP inicial:
- ServiceNow/ITSM;
- integrações automáticas com operadoras;
- webhooks e notificações;
- analytics avançado;
- SLA configurável;
- PWA/mobile;
- LLM/RAG/agentes NOC;
- classificação ou geração automática de comunicados.
