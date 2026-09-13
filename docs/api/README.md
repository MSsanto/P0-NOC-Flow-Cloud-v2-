# API Documentation

Este diretório organiza contratos, convenções, autenticação, erros e exemplos da API do P0 — NOC Flow Cloud v2.

## Referências atuais

- [Contrato geral da API v1](../06-API-CONTRACT.md)
- [Incidentes — contrato executado na Sprint 2](SPRINT_02-INCIDENTS.md)
- OpenAPI executável em `/api/v1/openapi.json` quando a aplicação está em execução
- Swagger em `/api/v1/docs`

## Estado atual

Até a Sprint 2 estão implementados os fluxos de criação/listagem/detalhe, atualização operacional, normalização, timeline e consulta avançada com filtros/paginação/ordenação.

OIDC/RBAC e identidade confiável ainda não estão implementados; a API permanece homologável apenas em ambiente local/teste.

## Regra de manutenção

Nenhuma mudança de contrato deve ser documentada como concluída antes de estar alinhada com Backend, Frontend e QA. Em caso de divergência, o OpenAPI e o comportamento testado devem ser reconciliados com esta documentação antes do fechamento da Sprint.
