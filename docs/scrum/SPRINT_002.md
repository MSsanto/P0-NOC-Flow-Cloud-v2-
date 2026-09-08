# Sprint 002 — Identidade, tenant e persistência

**Status:** Planejamento futuro  
**Período:** a definir no Sprint Planning  
**Sprint Goal proposto:** estabelecer persistência, identidade e isolamento multi-tenant como base segura para a primeira funcionalidade de incidente.

> Este documento contém backlog candidato e não representa compromisso antecipado. O conteúdo deve ser refinado após os resultados da Sprint 001.

## Backlog candidato

### P1-003 — Migrations
- implementar schema inicial;
- permitir reconstrução do banco a partir de migrations;
- documentar estratégia de rollback/downgrade.

### P1-004 — Identidade
- mapear identidade autenticada para usuário interno;
- impedir confiança em campos de identidade enviados pelo frontend;
- definir comportamento de autenticação para ambiente de desenvolvimento/demo conforme arquitetura aprovada.

### P1-005 — Tenant e membership
- modelar associação usuário/tenant;
- disponibilizar listagem apenas de tenants autorizados;
- propagar tenant context de forma segura;
- criar testes de isolamento cross-tenant.

### Preparação para P1-006 / P1-007
- validar contratos necessários para site, severidade e incidente;
- revisar dependências de dados e UX;
- garantir que histórias atendam à Definition of Ready antes de ingressarem em Sprint.

## Dependências

- Sprint 001 concluída ou base executável equivalente disponível;
- ORM/migration stack definida;
- estratégia de IDs aprovada;
- estratégia de autenticação/OIDC registrada;
- modelo de dados revisado por Database & Data Model;
- regras de autorização revisadas por Security/AppSec.

## Critérios de sucesso da Sprint

- banco é recriável por migrations;
- identidade do usuário é determinada de forma confiável pelo backend;
- usuário acessa somente tenants autorizados;
- teste automatizado comprova ausência de vazamento cross-tenant no escopo implementado;
- erros relevantes possuem resposta e logging adequados;
- pipeline permanece verde;
- documentação técnica e OpenAPI são atualizadas conforme mudanças.

## Riscos / impedimentos iniciais

| Item | Impacto | Tratamento |
|---|---|---|
| Autorização baseada apenas no frontend | Crítico | autorização obrigatória no backend e testes negativos |
| Tenant scoping inconsistente | Crítico | contexto centralizado + testes cross-tenant |
| Migration sem rollback documentado | Médio | revisão de Database/Backend antes de Done |
| Dependência prematura de provedor de identidade cloud | Médio | abstração e modo local conforme ADR |

## Evidências da Sprint

A preencher durante a Sprint:

- Pull Requests:
- migrations:
- testes unitários:
- testes de integração:
- testes cross-tenant:
- security review:
- documentação atualizada:

## Sprint Review

A preencher ao final:

- itens concluídos:
- itens não concluídos:
- demonstração realizada:
- feedback dos stakeholders:
- alterações propostas ao Product Backlog:

## Retrospective

Registrar conclusões consolidadas em [RETROSPECTIVES.md](RETROSPECTIVES.md).