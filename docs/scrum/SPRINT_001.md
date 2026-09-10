# Sprint 001 — Fundação Executável

**Status:** Concluída tecnicamente  
**Período de execução:** 2026-09-08 a 2026-09-10  
**Release alvo:** `v0.1.0-alpha`  
**Sprint Goal:** entregar uma base executável, testável e reproduzível com Angular, FastAPI e PostgreSQL, incluindo o primeiro vertical slice de incidentes.

## Modelo operacional da Sprint

A execução principal, refinamento, documentação e coordenação desta Sprint são centralizados no workspace principal do projeto. As disciplinas abaixo indicam responsabilidades técnicas, não a necessidade de manter chats separados. Revisão independente, QA/homologação e auditorias especializadas podem ser executadas separadamente quando a independência agregar valor.

## User Stories

### US-001 — Listar incidentes [P0]
**Disciplina primária:** Frontend  
**Dependências:** EN-001, EN-002, EN-003, EN-004  
**Resultado:** CONCLUÍDA

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
**Resultado:** CONCLUÍDA

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
- tenant/ator da Sprint 1 usam provider de desenvolvimento/demo explicitamente isolado e sintético, sem antecipar OIDC/RBAC da Sprint 3.

**Fora da Sprint 1:** unidade/site estruturado, severidade configurável, origem, anexos, SLA, operadora, protocolos externos, timeline/evento `INCIDENT_CREATED`, notificações e automações.

### US-003 — Visualizar detalhe [P0]
**Disciplina primária:** Frontend  
**Dependências:** US-001, US-002  
**Resultado:** CONCLUÍDA

Como operador NOC, quero abrir os detalhes de um incidente para analisar todas as informações registradas sobre ele.

**Aceite:**
- rota por ID;
- consulta via API;
- tratamento de ID inexistente;
- refresh preserva rota/contexto;
- dados completos da versão inicial exibidos;
- acesso permanece limitado ao tenant do contexto autorizado.

## Enablers e resultado

| ID | Entrega | Resultado |
|---|---|---|
| EN-001 | Arquitetura baseline + ADRs | Done |
| EN-002 | Database foundation + migrations | Done |
| EN-003 | Backend FastAPI foundation | Done |
| EN-004 | Frontend Angular foundation | Done |
| EN-005 | Docker Compose + CI | Done |
| EN-006 | Escopo MVP e critérios funcionais | Done |
| EN-007 | UX foundation do fluxo de incidentes | Done |
| EN-008 | Threat model e security baseline | Done para alpha local/teste |
| EN-009 | Estratégia e suíte de testes S1 | Done |
| EN-010 | Documentação da Sprint e setup | fechamento documental |
| EN-011 | Code Review independente | Done; 1 MAJOR corrigido |
| EN-012 | Homologação da `v0.1.0-alpha` | gate final após documentação |

## Task Breakdown executado

### Produto
- TASK-PO-001 campos/regras mínimas de criação;
- TASK-PO-002 aceite de US-001/002/003;
- TASK-PO-003 itens fora da Sprint.

### Architecture
- arquitetura Angular/FastAPI;
- modular monolith;
- `/api/v1`;
- Problem Details/error handling;
- estratégia multi-tenant;
- ADRs essenciais.

### UX/UI
- fluxo lista → criar → detalhe;
- formulário e validações;
- loading/empty/error/success;
- responsividade e acessibilidade.

### Frontend
- listagem e estados;
- integração GET;
- formulário e validações;
- integração POST;
- rota e tela de detalhe;
- bootstrap, routing, shell, environments, HttpClient e error handling.

### Backend
- endpoints de listagem, criação e detalhe;
- services/repository;
- schema canônico;
- persistência;
- bootstrap, settings, SQLAlchemy, DI, exceptions, health e OpenAPI.

### Database
- PostgreSQL local;
- Alembic/migration inicial;
- Tenant e Incident;
- PK/FK/constraints;
- índices tenant-scoped.

### QA
- testes de API;
- testes frontend;
- criação válida e inválida;
- detalhe/404;
- smoke funcional FE+BE+DB.

### DevOps
- Dockerfile frontend/backend;
- PostgreSQL;
- Docker Compose;
- GitHub Actions com lint → tests → build → security checks → functional smoke.

### Security
- threat model inicial;
- CORS e configuração segura;
- secrets/`.env`;
- tenant isolation;
- revisão OWASP API do vertical slice;
- headers de segurança no Nginx.

### Documentation
- README/setup atualizado;
- Sprint 001 e resumo de evidências;
- API/Architecture/Security sincronizados;
- evidências de portfólio e roteiro de homologação.

### Code Review independente
- frontend, backend e migrations revisados;
- classificação BLOCKER/MAJOR/MINOR/SUGGESTION;
- MAJOR de consistência de validação FE/BE corrigido no PR #29;
- 0 BLOCKER/MAJOR pendente para a alpha.

## Definition of Ready aplicada

O contrato da US-002 foi consolidado antes do vertical slice executável. O P0 Gate e o blocker de contrato foram fechados antes da conclusão da Sprint.

## Critérios de sucesso — resultado

- `docker compose` sobe frontend, backend e banco: **PASS**;
- healthcheck funcional: **PASS**;
- criar/listar/detalhar ponta a ponta: **PASS**;
- CI: **PASS**;
- testes críticos: **PASS**;
- nenhum BLOCKER de review: **PASS**;
- nenhum Critical/High sem mitigação no escopo alpha: **PASS**;
- documentação reflete o estado real: **PASS após merge do fechamento documental**;
- homologação: executada em EN-012 após o gate documental.

## Evidências principais

- PR #16 — backend do vertical slice;
- PR #25 — frontend US-001/002/003;
- PR #26 — QA smoke funcional;
- PR #27 — AppSec;
- PR #29 — correção de code review;
- CI #33 `34392403933` — jornada full-stack verde;
- CI #34 `34392517493` — security/audits/Compose verdes;
- CI #39 `34528173526` — regressão completa após correção de review.

Para o histórico detalhado de execução, consulte [`../sprints/SPRINT_01.md`](../sprints/SPRINT_01.md). Para reprodução do aceite, consulte [`../releases/V0.1.0-ALPHA-HOMOLOGATION.md`](../releases/V0.1.0-ALPHA-HOMOLOGATION.md).

## Limite da aprovação

A Sprint 1 entrega uma **alpha local/teste**. OIDC/RBAC e identidade confiável ainda não fazem parte do incremento. Portanto, conclusão/homologação desta Sprint não autoriza deploy público ou produção.
