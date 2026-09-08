# Scrum — P0 NOC Flow Cloud v2

Este diretório é a fonte canônica dos artefatos de gestão de produto e Scrum do projeto.

## Documentos

- [PRODUCT_VISION.md](PRODUCT_VISION.md) — visão, personas, proposta de valor e escopo do MVP.
- [PRODUCT_BACKLOG.md](PRODUCT_BACKLOG.md) — backlog priorizado do produto.
- [ROADMAP.md](ROADMAP.md) — roadmap oficial em 6 Sprints.
- [DEFINITION_OF_READY.md](DEFINITION_OF_READY.md) — critérios mínimos para uma história entrar em Sprint Planning.
- [DEFINITION_OF_DONE.md](DEFINITION_OF_DONE.md) — critérios obrigatórios para considerar trabalho concluído.
- [SPRINT_001.md](SPRINT_001.md) — Fundação Executável (`v0.1.0-alpha`).
- [SPRINT_002.md](SPRINT_002.md) — Incidentes & Timeline (`v0.2.0-alpha`).
- [SPRINT_003.md](SPRINT_003.md) — Auth, RBAC & Multi-Tenancy (`v0.3.0-beta`).
- [SPRINT_004.md](SPRINT_004.md) — Dashboard & Passagem de Turno (`v0.4.0-beta`).
- [SPRINT_005.md](SPRINT_005.md) — Auditoria & Observabilidade (`v0.5.0-rc1`).
- [SPRINT_006.md](SPRINT_006.md) — Azure & Release (`v1.0.0`).
- [RETROSPECTIVES.md](RETROSPECTIVES.md) — histórico consolidado de retrospectivas.

## Governança

- Product Owner é responsável por visão, prioridade e critérios de aceite.
- Scrum Master/Orchestrator coordena planning, dependências, impedimentos, review, retrospective e encaminhamento aos especialistas.
- Especialistas técnicos executam somente itens compatíveis com sua função e respeitam decisões arquiteturais/funcionais aprovadas.
- QA, Security, Documentation, Code Review e Release são quality gates transversais e não atividades apenas de fim de projeto.
- Technical Writer mantém consistência, links, histórico e legibilidade da documentação.
- Alterações de arquitetura devem ser registradas também em `../adr/` quando aplicável.

## Fluxo de trabalho

`Product Backlog → Sprint → Implementação → QA → Code Review → Documentação → Homologação → Done`

Itens bloqueados devem registrar impedimento e retornar ao especialista responsável. Um item não deve ser marcado Done sem atender à Definition of Done.

## Status

A Sprint 001 está em planejamento ativo. Sprints 002–006 são planejamento futuro e podem ser refinadas conforme feedback, capacidade e resultados das Sprints anteriores.
