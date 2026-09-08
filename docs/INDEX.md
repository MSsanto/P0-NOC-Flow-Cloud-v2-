# Índice da documentação — P0 NOC Flow Cloud v2

A documentação é organizada por domínio para facilitar navegação por desenvolvedores, QA, segurança, Tech Leads, recrutadores e usuários técnicos.

## Produto e Scrum

Fonte canônica: [`docs/scrum/`](scrum/README.md)

- [Product Vision](scrum/PRODUCT_VISION.md)
- [Product Backlog](scrum/PRODUCT_BACKLOG.md)
- [Roadmap](scrum/ROADMAP.md)
- [Definition of Ready](scrum/DEFINITION_OF_READY.md)
- [Definition of Done](scrum/DEFINITION_OF_DONE.md)
- [Sprint 001](scrum/SPRINT_001.md)
- [Sprint 002](scrum/SPRINT_002.md)
- [Retrospectives](scrum/RETROSPECTIVES.md)

## Arquitetura

- [Índice de arquitetura](architecture/README.md)
- [Arquitetura atual](03-ARCHITECTURE.md)
- [Modelo de domínio](04-DOMAIN-MODEL.md)
- [Modelo lógico de dados](05-DATA-MODEL.md)
- [DevOps e Azure](10-DEVOPS-AZURE.md)
- [Observabilidade](11-OBSERVABILITY.md)
- [Plano de implementação](16-IMPLEMENTATION-PLAN.md)
- [Matriz de rastreabilidade](17-TRACEABILITY.md)

## Architecture Decision Records

- [Índice de ADRs](adr/README.md)
- [ADR-0001 — Stack e modular monolith](adr/0001-stack-and-modular-monolith.md)
- [ADR-0002 — Multi-tenancy](adr/0002-multitenancy.md)
- [ADR-0003 — Lifecycle do incidente](adr/0003-incident-lifecycle.md)
- [ADR-0004 — Identidade OIDC](adr/0004-identity.md)
- [ADR-0005 — Política de dados públicos](adr/0005-public-data-policy.md)

## API

- [Índice da API](api/README.md)
- [Contrato conceitual da API v1](06-API-CONTRACT.md)

## UX

- [Índice de UX](ux/README.md)
- [UX e fluxos](07-UX-FLOWS.md)

## Segurança

- [Índice técnico de segurança](security/README.md)
- [Segurança e privacidade](08-SECURITY-PRIVACY.md)
- [Política pública de segurança](../SECURITY.md)

## Qualidade e requisitos

- [Project Charter](00-PROJECT-CHARTER.md)
- [Requisitos](02-REQUIREMENTS.md)
- [Estratégia de testes](09-TEST-STRATEGY.md)
- [Riscos](15-RISKS.md)
- [Glossário](GLOSSARY.md)

## Governança do repositório

- [README principal](../README.md)
- [CONTRIBUTING](../CONTRIBUTING.md)
- [SECURITY](../SECURITY.md)
- [CHANGELOG](../CHANGELOG.md)
- [LICENSE](../LICENSE.md)
- [Pull Request template](../.github/pull_request_template.md)

## Regra documental

A documentação deve refletir o comportamento e as decisões reais do projeto. Se a implementação divergir, a mudança deve atualizar o documento correspondente e, quando houver decisão arquitetural relevante, criar ou superseder um ADR.

Arquivos numerados antigos que apontam para documentos em `scrum/` são mantidos somente para compatibilidade de links históricos; a fonte canônica é sempre o arquivo indicado no novo diretório.