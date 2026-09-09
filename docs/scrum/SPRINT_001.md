# Sprint 001 — Fundação Executável

**Status:** Em execução  
**Duração planejada:** 2 semanas  
**Release alvo:** `v0.1.0-alpha`  
**Sprint Goal:** entregar uma base executável, testável e reproduzível com Angular, FastAPI e PostgreSQL, incluindo o primeiro vertical slice de incidentes.

## Modelo operacional da Sprint

A execução principal, refinamento, documentação e coordenação desta Sprint são centralizados no workspace principal do projeto. As disciplinas abaixo indicam responsabilidades técnicas, não a necessidade de manter chats separados. Revisão independente, QA/homologação e auditorias especializadas podem ser executadas separadamente quando a independência agregar valor.

## User Stories

### US-001 — Listar incidentes [P0]
**Disciplina primária:** Frontend  
**Dependências:** EN-001, EN-002, EN-003, EN-004

Como operador NOC, quero visualizar os incidentes registrados para identificar rapidamente o estado atual da operação.

**Aceite:**
- dados consumidos da API real, sem mock na entrega;
- cada item exibe ID, título, recurso/serviço afetado, status, severidade e início do incidente;
- ordenação padrão: incidentes mais recentes primeiro;
- estados loading, vazio e erro claramente distintos;
- erro permite nova tentativa sem recarregar toda a aplicação;
- seleção de um item conduz ao detalhe do incidente;
- listagem respeita o tenant do contexto autorizado.

**Fora da Sprint 1:** filtros avançados, busca textual, SLA e dashboards agregados.

### US-002 — Criar incidente [P0]
**Disciplina primária:** Backend  
**Dependências:** US-001, UX, modelo Incident, contrato API

Como operador NOC, quero registrar um novo incidente para documentar formalmente uma indisponibilidade ou degradação.

**Campos obrigatórios canônicos:**
- `title`: 3–120 caracteres;
- `affected_resource`: 2–120 caracteres;
- `severity`: `CRITICAL | HIGH | MEDIUM | LOW`;
- `impact_type`: `OUTAGE | DEGRADATION`;
- `symptoms`: 10–2000 caracteres;
- `started_at`: data/hora ISO-8601, não posterior ao momento do registro.

**Gerados/resolvidos pelo sistema:** `id`, status inicial `OPEN`, `tenant_id`, ator/criador, `created_at` e `updated_at`.

**Aceite:**
- frontend e backend validam obrigatórios e limites;
- persistência PostgreSQL sem registro parcial;
- tenant e autor não são informados manualmente como autoridade do body;
- ID e timestamps são automáticos;
- sucesso retorna `201 Created` com o incidente criado;
- entrada inválida retorna Problem Details consistente e não cria incidente;
- tenant/ator da Sprint 1 podem usar provider de desenvolvimento/demo explicitamente isolado e sintético, sem antecipar OIDC/RBAC da Sprint 3.

**Fora da Sprint 1:** unidade/site estruturado, severidade configurável, origem, anexos, SLA, operadora, protocolos externos, timeline/evento `INCIDENT_CREATED`, notificações e automações.

### US-003 — Visualizar detalhe [P0]
**Disciplina primária:** Frontend  
**Dependências:** US-001, US-002

Como operador NOC, quero abrir os detalhes de um incidente para analisar todas as informações registradas sobre ele.

**Aceite:**
- rota por ID;
- consulta via API;
- tratamento de ID inexistente;
- refresh preserva rota/contexto;
- dados completos da versão inicial exibidos;
- acesso permanece limitado ao tenant do contexto autorizado.

## Enablers e disciplinas

| ID | Entrega | Disciplina primária |
|---|---|---|
| EN-001 | Arquitetura baseline + ADRs | Software Architecture |
| EN-002 | Database foundation + migrations | Database & Data Model |
| EN-003 | Backend FastAPI foundation | Backend & API |
| EN-004 | Frontend Angular foundation | Frontend |
| EN-005 | Docker Compose + CI inicial | DevOps, Azure & CI/CD |
| EN-006 | Escopo MVP e critérios funcionais | Product Owner / Produto |
| EN-007 | UX foundation do fluxo de incidentes | UX/UI |
| EN-008 | Threat model e security baseline | Security & AppSec |
| EN-009 | Estratégia e suíte de testes S1 | QA & Automated Tests |
| EN-010 | Documentação da Sprint e setup | Documentation & Portfolio |
| EN-011 | Code Review independente | Code Review & Refactoring |
| EN-012 | Homologação da `v0.1.0-alpha` | Releases & Homologation |

## Task Breakdown

### Produto
- TASK-PO-001 definir campos/regras mínimas de criação de incidente;
- TASK-PO-002 validar US-001/002/003 e critérios de aceite;
- TASK-PO-003 confirmar escopo fora da Sprint.

### Architecture
- TASK-ARC-001 arquitetura Angular;
- TASK-ARC-002 arquitetura FastAPI;
- TASK-ARC-003 modular monolith;
- TASK-ARC-004 `/api/v1`;
- TASK-ARC-005 error handling;
- TASK-ARC-006 estratégia multi-tenant;
- TASK-ARC-007 ADRs essenciais.

### UX/UI
- TASK-UX-001 fluxo lista → criar → detalhe;
- TASK-UX-002 formulário e validações;
- TASK-UX-003 loading/empty/error/success;
- TASK-UX-004 especificação responsiva e acessível.

### Frontend
- TASK-FE-001 listagem de incidentes;
- TASK-FE-002 estados da listagem;
- TASK-FE-003 integração GET incidents;
- TASK-FE-004 formulário;
- TASK-FE-005 validações;
- TASK-FE-006 integração POST incident;
- TASK-FE-007 rota detalhe;
- TASK-FE-008 tela detalhe;
- TASK-FE-009..014 bootstrap, routing, shell, environment, HttpClient e error handling.

### Backend
- TASK-BE-001 endpoint de listagem;
- TASK-BE-002 service/repository de consulta;
- TASK-BE-003 schema de criação;
- TASK-BE-004 service de criação;
- TASK-BE-005 persistência;
- TASK-BE-006 endpoint de detalhe;
- TASK-BE-007..013 bootstrap, settings, SQLAlchemy, DI, exceptions, health e OpenAPI.

### Database
- TASK-DB-001 suporte à listagem;
- TASK-DB-002 persistência de Incident;
- TASK-DB-003 PostgreSQL local;
- TASK-DB-004 migrations;
- TASK-DB-005 Tenant;
- TASK-DB-006 Incident;
- TASK-DB-007 constraints;
- TASK-DB-008 índices essenciais.

### QA
- TASK-QA-001 testes API listagem;
- TASK-QA-002 testes frontend listagem;
- TASK-QA-003 criação válida;
- TASK-QA-004 criação inválida/negativa;
- TASK-QA-005 detalhe/404;
- TASK-QA-006 smoke test FE+BE+DB.

### DevOps
- TASK-DO-001 Dockerfile frontend;
- TASK-DO-002 Dockerfile backend;
- TASK-DO-003 serviço PostgreSQL;
- TASK-DO-004 docker-compose;
- TASK-DO-005 GitHub Actions: lint → tests → build → security checks.

### Security
- TASK-SEC-001 threat model inicial;
- TASK-SEC-002 CORS e configuração segura;
- TASK-SEC-003 secrets e `.env`;
- TASK-SEC-004 riscos de tenant isolation;
- TASK-SEC-005 revisão OWASP API do vertical slice.

### Documentation
- TASK-DOC-001 atualizar README/setup;
- TASK-DOC-002 manter Sprint 001;
- TASK-DOC-003 atualizar API/Architecture/Security impactados;
- TASK-DOC-004 registrar evidências para portfólio.

### Code Review independente
- TASK-CR-001 revisar FE;
- TASK-CR-002 revisar BE;
- TASK-CR-003 revisar migrations/DB;
- TASK-CR-004 classificar BLOCKER/MAJOR/MINOR/SUGGESTION.

### Release / Homologação
- TASK-REL-001 validar build e CI;
- TASK-REL-002 smoke da jornada criar/listar/detalhar;
- TASK-REL-003 validar testes/security/docs;
- TASK-REL-004 emitir decisão de homologação.

## Dependências críticas

`Produto/contrato → Architecture → UX / DB / Security → Backend + Frontend → DevOps → QA → Review independente → Docs → Release`

## Definition of Ready aplicada

Uma história só entra em execução quando objetivo, aceite, dependências, contrato necessário e decisão arquitetural relevante estiverem definidos.

Com a resolução do contrato da US-002, US-001/002/003 ficam funcionalmente refinadas para implementação. A conclusão continua dependente das fundações executáveis, migrations, CI e testes.

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

Evidências atuais e futuras devem registrar PRs, builds, testes, security checks, demo, bugs, feedback, itens concluídos/não concluídos e ações de retrospectiva. O Trello acompanha o estado operacional dos cards; este documento mantém o contrato e o histórico da Sprint.
