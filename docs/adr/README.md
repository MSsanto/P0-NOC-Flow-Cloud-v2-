# Architecture Decision Records — P0 NOC Flow Cloud v2

Este diretório registra decisões arquiteturais relevantes e seus trade-offs.

## ADRs atuais

- [ADR-0001 — Stack e modular monolith](0001-stack-and-modular-monolith.md)
- [ADR-0002 — Multi-tenancy](0002-multitenancy.md)
- [ADR-0003 — Lifecycle do incidente](0003-incident-lifecycle.md)
- [ADR-0004 — Identidade OIDC](0004-identity.md)
- [ADR-0005 — Política de dados públicos](0005-public-data-policy.md)
- [ADR-0006 — Versionamento da API e contrato uniforme de erros](0006-api-versioning-and-errors.md)

## Quando criar um ADR

Criar ou atualizar um ADR quando houver decisão duradoura envolvendo arquitetura, segurança, persistência, autenticação, integração, cloud, padrões de comunicação, estrutura de módulos ou outro trade-off relevante para manutenção do sistema.

## Estrutura recomendada

1. Status
2. Contexto
3. Decisão
4. Alternativas consideradas
5. Consequências
6. Referências

## Status possíveis

- Proposed
- Accepted
- Superseded
- Deprecated

ADRs aceitos não devem ser reescritos para apagar o histórico. Quando uma decisão for substituída, o ADR anterior deve indicar qual novo ADR o supersede.
