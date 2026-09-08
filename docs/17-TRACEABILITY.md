# Matriz de rastreabilidade

Objetivo: provar que requisitos essenciais possuem trabalho planejado e teste correspondente.

| Requisito | Backlog principal | Evidência de teste planejada |
|---|---|---|
| RF-001 Autenticação | P1-004 | integração identity + E2E login demo |
| RF-002 Tenant authz | P1-005 | testes cross-tenant |
| RF-003 Papéis | P2-015 | permission unit + API integration |
| RF-004 Base operacional | P1-006/P2-004 | CRUD integration |
| RF-005 Incidente | P1-007 | domain + API integration |
| RF-006 Correlação | P2-005 | unit + cenários de janela |
| RF-007 Timeline | P1-007/P2-001 | ordem e imutabilidade |
| RF-008 Atualização | P2-002 | API + E2E |
| RF-009 Normalização | P2-006 | transição + E2E |
| RF-010 Reabertura | P2-007 | permission/state tests |
| RF-011 Templates | P2-008/P2-009 | snapshot/version tests |
| RF-012 Handover | P2-012/P2-013 | snapshot/version tests |
| RF-013 Busca | P2-011 | query integration |
| RF-014 Dashboard | P2-010 | API aggregation + UI |
| RF-015 Auditoria | P2-014 | audit transaction tests |
| RF-016 Exportação | P2-016 | authz + audit |
| RF-017 Demo sintética | P2-019 | public-data validation |
| RF-018 API versionada | P1 | contract/OpenAPI check |
| RNF-002 Isolamento | P1-005 | suite obrigatória cross-tenant |
| RNF-005 Acessibilidade | P2-018 | automated + keyboard manual |
| RNF-007 Observabilidade | P1/P3 | request-id/health/metrics checks |

## Uso

Ao alterar um requisito:

1. atualizar `02-REQUIREMENTS.md`;
2. revisar backlog afetado;
3. revisar testes esperados;
4. criar ADR se houver mudança arquitetural;
5. atualizar esta matriz.