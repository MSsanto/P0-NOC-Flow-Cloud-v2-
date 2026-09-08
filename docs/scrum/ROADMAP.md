# Roadmap — P0 NOC Flow Cloud v2

## P0 — Fundação documental

**Objetivo:** tornar o projeto implementável sem decisões essenciais implícitas.

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
- [x] estrutura documental Scrum;
- [ ] revisão final dos ADRs;
- [ ] aprovação para iniciar P1.

## P1 — Core vertical

**Objetivo:** entregar a primeira fatia executável ponta a ponta.

1. scaffold do repositório;
2. PostgreSQL + migrations;
3. autenticação abstraída + usuário de demonstração;
4. tenants/memberships;
5. sites/severidades;
6. criar/listar/detalhar incidente;
7. timeline básica;
8. testes cross-tenant;
9. Angular consumindo API real;
10. CI inicial.

**Demo de saída:** usuário entra em tenant fictício, cria incidente e consulta timeline persistida.

## P2 — Operação completa do MVP

- circuitos e operadoras;
- atualização do incidente;
- protocolos;
- normalização e reabertura;
- templates e comunicados;
- dashboard operacional;
- passagem de turno;
- busca e filtros;
- administração;
- auditoria;
- acessibilidade e refinamento de UX;
- suíte E2E crítica.

## P3 — Cloud e qualidade operacional

- Dockerfiles finais;
- Infrastructure as Code;
- Azure dev/demo;
- GitHub Actions completo;
- Key Vault / Managed Identity quando aplicável;
- Application Insights;
- migrations e deploy seguro;
- smoke tests;
- backup/restore de demonstração;
- runbook e rollback;
- controle de custo.

## P4 — Integrações

- webhook de monitoramento;
- normalização de eventos;
- correlação avançada;
- adapter ITSM;
- webhooks de saída;
- filas/retries/DLQ quando justificados;
- notificações assistidas.

## P5 — Evoluções opcionais

- SSO corporativo específico;
- analytics avançado;
- regras configuráveis de SLA;
- importação em massa;
- feature flags;
- PWA/mobile mediante necessidade comprovada;
- assistência por IA somente com guardrails, explicabilidade e revisão humana.

## Regra de evolução

O roadmap descreve direção e sequência esperada, não compromisso fixo de datas. Mudanças de prioridade devem ser refletidas no [Product Backlog](PRODUCT_BACKLOG.md) e, quando relevantes, registradas nas Sprints correspondentes.