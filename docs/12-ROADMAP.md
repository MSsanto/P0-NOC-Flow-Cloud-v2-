# Roadmap

## P0 — Fundação documental — atual

Entregáveis:

- [x] charter;
- [x] visão;
- [x] requisitos;
- [x] arquitetura;
- [x] domínio;
- [x] modelo de dados;
- [x] API conceitual;
- [x] UX flows;
- [x] segurança;
- [x] estratégia de testes;
- [x] Azure/DevOps;
- [x] observabilidade;
- [x] backlog;
- [x] Definition of Done;
- [x] riscos;
- [ ] revisão final dos ADRs;
- [ ] aprovação para iniciar P1.

## P1 — Core vertical

Objetivo: primeira fatia executável ponta a ponta.

1. monorepo/scaffold;
2. PostgreSQL + migrations;
3. auth abstraída + usuário demo;
4. tenants/memberships;
5. sites/severities;
6. criar/listar incidente;
7. timeline básica;
8. testes cross-tenant;
9. Angular consumindo API.

**Demo de saída:** usuário entra em tenant fictício, cria incidente e consulta timeline persistida.

## P2 — Operação completa do MVP

- circuitos/operadoras;
- atualização;
- protocolos;
- normalização/reabertura;
- templates/comunicados;
- dashboard;
- passagem de turno;
- busca/filtros;
- administração;
- auditoria;
- acessibilidade e UX refinada.

## P3 — Cloud e qualidade operacional

- Dockerfiles finais;
- IaC;
- Azure dev/demo;
- GitHub Actions completo;
- Key Vault/Managed Identity quando aplicável;
- Application Insights;
- migrations/deploy seguro;
- backup/restore de demonstração;
- documentação de runbook.

## P4 — Integrações

- webhook de monitoramento;
- normalização de eventos;
- correlação avançada;
- adapter ITSM;
- webhooks de saída;
- filas/retries/DLQ se necessários;
- notificações assistidas.

## P5 — Evoluções opcionais

- SSO corporativo específico;
- analytics avançado;
- regras configuráveis de SLA;
- importação em massa;
- feature flags;
- mobile/PWA se houver necessidade comprovada;
- assistência por IA somente com guardrails, explicabilidade e revisão humana.