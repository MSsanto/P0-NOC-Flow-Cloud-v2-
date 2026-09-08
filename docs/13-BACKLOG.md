# Backlog priorizado

Legenda: `P0` obrigatório antes de código; `P1` core; `P2` MVP operacional; `P3` cloud; `P4` integração.

## P0 — Arquitetura e governança

- [x] P0-001 Definir objetivo e escopo.
- [x] P0-002 Definir personas/JTBD.
- [x] P0-003 Definir stack inicial.
- [x] P0-004 Definir modular monolith.
- [x] P0-005 Definir estratégia multi-tenant.
- [x] P0-006 Definir estados de incidente.
- [x] P0-007 Definir modelo lógico.
- [x] P0-008 Definir API v1 conceitual.
- [x] P0-009 Definir UX prioritária.
- [x] P0-010 Definir segurança e publicação segura.
- [x] P0-011 Definir testes.
- [x] P0-012 Definir Azure/CI/CD.
- [x] P0-013 Definir observabilidade.
- [x] P0-014 Definir Definition of Done.
- [x] P0-015 Registrar riscos.
- [ ] P0-016 Revisar ADRs e aprovar início P1.

## P1 — Fundação técnica

### P1-001 Scaffold do monorepo
**Aceite:** diretórios web/api/infra/tests; scripts documentados; lockfiles versionados.

### P1-002 Ambiente local
**Aceite:** API e PostgreSQL sobem com fluxo documentado; health check responde.

### P1-003 Migrations
**Aceite:** schema inicial recriável do zero e downgrade/rollback strategy documentada.

### P1-004 Identidade
**Aceite:** usuário autenticado é mapeado internamente; API não confia em identity fields enviados pelo front.

### P1-005 Tenant/membership
**Aceite:** usuário só lista tenants autorizados; teste automatizado prova isolamento.

### P1-006 Base mínima
**Aceite:** CRUD controlado de site e severidade com tenant scoping.

### P1-007 Criar incidente
**Aceite:** criação válida gera incidente + evento `INCIDENT_CREATED` atomicamente.

### P1-008 Listar/detalhar incidente
**Aceite:** filtros básicos; recurso de outro tenant retorna resposta segura.

### P1-009 Front vertical
**Aceite:** Angular seleciona tenant, lista e cria incidente sem mocks de API no caminho principal.

### P1-010 CI inicial
**Aceite:** lint, tests e build executam em PR.

## P2 — Incidente operacional

- [ ] P2-001 acknowledge e transições;
- [ ] P2-002 atualização estruturada;
- [ ] P2-003 protocolos/ITSM IDs;
- [ ] P2-004 circuitos e operadoras;
- [ ] P2-005 sugestão de duplicidade/correlação;
- [ ] P2-006 resolução/normalização;
- [ ] P2-007 reabertura com justificativa;
- [ ] P2-008 templates versionados;
- [ ] P2-009 renderização de alert/update/normalization;
- [ ] P2-010 dashboard acionável;
- [ ] P2-011 busca avançada;
- [ ] P2-012 passagem de turno preview;
- [ ] P2-013 finalizar/versionar handover;
- [ ] P2-014 auditoria;
- [ ] P2-015 RBAC administrativo;
- [ ] P2-016 exportação segura;
- [ ] P2-017 tema claro/escuro;
- [ ] P2-018 acessibilidade WCAG nos fluxos críticos;
- [ ] P2-019 seed público sintético;
- [ ] P2-020 suíte E2E crítica.

## P3 — Azure/produção de demo

- [ ] P3-001 Docker API;
- [ ] P3-002 IaC;
- [ ] P3-003 PostgreSQL Azure;
- [ ] P3-004 hospedagem Angular;
- [ ] P3-005 Container Apps/API;
- [ ] P3-006 secrets/Key Vault;
- [ ] P3-007 Application Insights;
- [ ] P3-008 GitHub Actions deploy;
- [ ] P3-009 smoke tests pós-deploy;
- [ ] P3-010 runbook e rollback;
- [ ] P3-011 orçamento/alerta de custo.

## P4 — Integrações

- [ ] P4-001 contrato de evento normalizado;
- [ ] P4-002 webhook autenticado;
- [ ] P4-003 idempotência;
- [ ] P4-004 correlação WAN/eventos;
- [ ] P4-005 adapter ITSM genérico;
- [ ] P4-006 adapter específico apenas em módulo privado/configurável;
- [ ] P4-007 retry/backoff;
- [ ] P4-008 dead-letter strategy;
- [ ] P4-009 webhook de saída;
- [ ] P4-010 métricas de integração.

## Dívida explicitamente proibida

Não aceitar como “temporário”:

- queries sem tenant scoping;
- secrets hard-coded;
- dados reais em fixtures;
- autorização apenas no front-end;
- transição de estado sem teste;
- exclusão de histórico para facilitar UI;
- números de produtividade inventados.