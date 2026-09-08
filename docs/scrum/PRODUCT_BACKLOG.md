# Product Backlog — P0 NOC Flow Cloud v2

> Fonte canônica do backlog priorizado do produto.

## Prioridades

- **P0 — Crítico:** necessário antes do início seguro do desenvolvimento.
- **P1 — Importante/Core:** primeira fatia funcional ponta a ponta.
- **P2 — MVP operacional:** completa o fluxo principal de operação NOC.
- **P3 — Cloud/Qualidade:** disponibilização e operação da demo em Azure.
- **P4 — Integrações:** integração progressiva com sistemas externos.

## P0 — Arquitetura e governança

- [x] **P0-001** Definir objetivo e escopo.
- [x] **P0-002** Definir personas e Jobs to be Done.
- [x] **P0-003** Definir stack inicial.
- [x] **P0-004** Definir arquitetura modular monolith.
- [x] **P0-005** Definir estratégia multi-tenant.
- [x] **P0-006** Definir estados de incidente.
- [x] **P0-007** Definir modelo lógico.
- [x] **P0-008** Definir API v1 conceitual.
- [x] **P0-009** Definir UX prioritária.
- [x] **P0-010** Definir segurança e publicação segura.
- [x] **P0-011** Definir estratégia de testes.
- [x] **P0-012** Definir Azure/CI/CD.
- [x] **P0-013** Definir observabilidade.
- [x] **P0-014** Definir Definition of Done.
- [x] **P0-015** Registrar riscos.
- [ ] **P0-016** Revisar ADRs e aprovar início do P1.

## P1 — Fundação técnica

### P1-001 — Scaffold do repositório
**Critério de aceite:** estrutura oficial versionada; scripts documentados; lockfiles versionados; nenhuma dependência de ambiente não documentada.

### P1-002 — Ambiente local
**Critério de aceite:** backend e PostgreSQL sobem com fluxo documentado; health check responde; execução local não depende da Azure.

### P1-003 — Migrations
**Critério de aceite:** schema inicial recriável do zero; estratégia de rollback/downgrade documentada.

### P1-004 — Identidade
**Critério de aceite:** usuário autenticado é mapeado internamente; backend não confia em campos de identidade fornecidos pelo frontend.

### P1-005 — Tenant e membership
**Critério de aceite:** usuário lista apenas tenants autorizados; teste automatizado comprova isolamento cross-tenant.

### P1-006 — Base operacional mínima
**Critério de aceite:** CRUD controlado de site e severidade com tenant scoping.

### P1-007 — Criar incidente
**Critério de aceite:** criação válida persiste incidente e evento `INCIDENT_CREATED` atomicamente.

### P1-008 — Listar e detalhar incidente
**Critério de aceite:** filtros básicos disponíveis; acesso a recurso de outro tenant retorna resposta segura.

### P1-009 — Frontend vertical
**Critério de aceite:** Angular permite selecionar tenant, listar, criar e detalhar incidente consumindo a API real no caminho principal.

### P1-010 — CI inicial
**Critério de aceite:** lint, testes e build são executados em Pull Request.

## P2 — Incidente operacional

- [ ] **P2-001** Acknowledge e transições de estado.
- [ ] **P2-002** Atualização estruturada.
- [ ] **P2-003** Protocolos/ITSM IDs.
- [ ] **P2-004** Circuitos e operadoras.
- [ ] **P2-005** Sugestão de duplicidade/correlação.
- [ ] **P2-006** Resolução/normalização.
- [ ] **P2-007** Reabertura com justificativa.
- [ ] **P2-008** Templates versionados.
- [ ] **P2-009** Renderização de alert/update/normalization.
- [ ] **P2-010** Dashboard acionável.
- [ ] **P2-011** Busca avançada.
- [ ] **P2-012** Passagem de turno — preview.
- [ ] **P2-013** Finalizar/versionar handover.
- [ ] **P2-014** Auditoria.
- [ ] **P2-015** RBAC administrativo.
- [ ] **P2-016** Exportação segura.
- [ ] **P2-017** Tema claro/escuro.
- [ ] **P2-018** Acessibilidade WCAG nos fluxos críticos.
- [ ] **P2-019** Seed público sintético.
- [ ] **P2-020** Suíte E2E crítica.

## P3 — Azure / produção de demonstração

- [ ] **P3-001** Docker backend.
- [ ] **P3-002** Infrastructure as Code.
- [ ] **P3-003** PostgreSQL Azure.
- [ ] **P3-004** Hospedagem Angular.
- [ ] **P3-005** Container Apps/API.
- [ ] **P3-006** Secrets/Key Vault.
- [ ] **P3-007** Application Insights.
- [ ] **P3-008** GitHub Actions para deploy.
- [ ] **P3-009** Smoke tests pós-deploy.
- [ ] **P3-010** Runbook e rollback.
- [ ] **P3-011** Orçamento/alerta de custo.

## P4 — Integrações

- [ ] **P4-001** Contrato de evento normalizado.
- [ ] **P4-002** Webhook autenticado.
- [ ] **P4-003** Idempotência.
- [ ] **P4-004** Correlação WAN/eventos.
- [ ] **P4-005** Adapter ITSM genérico.
- [ ] **P4-006** Adapter específico apenas em módulo privado/configurável.
- [ ] **P4-007** Retry/backoff.
- [ ] **P4-008** Dead-letter strategy.
- [ ] **P4-009** Webhook de saída.
- [ ] **P4-010** Métricas de integração.

## Dívida explicitamente proibida

Não aceitar como solução “temporária”:

- queries sem tenant scoping;
- secrets hard-coded;
- dados reais em fixtures ou documentação;
- autorização apenas no frontend;
- transição de estado sem teste;
- exclusão de histórico para simplificar UI;
- números de produtividade não medidos.

## Refinamento

Uma história somente deve ser considerada candidata à Sprint quando atender a [Definition of Ready](DEFINITION_OF_READY.md). Uma entrega somente é concluída quando atender a [Definition of Done](DEFINITION_OF_DONE.md).