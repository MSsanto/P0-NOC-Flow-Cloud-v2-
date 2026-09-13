# API de Incidentes — contrato executado na Sprint 2

Base: `/api/v1`

Este documento registra o comportamento implementado e validado na Sprint 2. O OpenAPI gerado pelo FastAPI permanece a referência executável.

## Listagem simples — retrocompatibilidade

`GET /incidents`

Retorna um array de incidentes do tenant ativo, ordenado pelo comportamento padrão do backend. Foi preservado para não quebrar o contrato da Sprint 1.

## Consulta avançada

`GET /incidents/query`

Parâmetros opcionais:

| Parâmetro | Valores/regras |
|---|---|
| `status` | `OPEN`, `ACKNOWLEDGED`, `INVESTIGATING`, `MONITORING`, `RESOLVED`, `CLOSED` |
| `severity` | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` |
| `started_from` | datetime ISO-8601 |
| `started_to` | datetime ISO-8601; não pode ser anterior a `started_from` |
| `page` | inteiro >= 1; padrão 1 |
| `page_size` | inteiro 1..100; padrão 25 |
| `sort` | `started_at` ou `updated_at`; padrão `started_at` |
| `order` | `asc` ou `desc`; padrão `desc` |

Resposta `200`:

```json
{
  "items": [],
  "page": 1,
  "page_size": 25,
  "total": 0
}
```

Parâmetros fora do contrato ou período invertido retornam `422`.

## Atualização operacional

`POST /incidents/{incident_id}/updates`

Request:

```json
{
  "message": "Operadora acionada; protocolo DEMO-123."
}
```

Regras:
- `message`: 3–2000 caracteres após normalização de espaços;
- incidente deve existir no tenant ativo;
- `RESOLVED` e `CLOSED` não aceitam nova atualização;
- ator, tenant e timestamp são definidos pelo servidor;
- sucesso incrementa `version` e grava `INCIDENT_UPDATED` na timeline.

Erros principais:
- `404`: incidente não encontrado no contexto autorizado;
- `409`: incidente não está ativo;
- `422`: payload inválido/campo extra não permitido.

## Normalização

`POST /incidents/{incident_id}/normalize`

Request:

```json
{
  "note": "Conectividade restabelecida e validada."
}
```

`note` é opcional; quando fornecida, aceita 3–2000 caracteres.

Regras:
- incidente deve existir no tenant ativo;
- transição suportada leva ao status `RESOLVED`;
- sucesso incrementa `version` e grava `INCIDENT_NORMALIZED`;
- segunda normalização ou normalização de incidente fechado retorna `409`;
- ator, tenant e timestamp são autoridade do servidor.

## Timeline

`GET /incidents/{incident_id}/timeline`

Retorna eventos em ordem cronológica.

Exemplo:

```json
[
  {
    "id": "uuid",
    "incident_id": "uuid",
    "event_type": "INCIDENT_CREATED",
    "message": null,
    "actor_subject": "demo-operator",
    "occurred_at": "2026-09-13T15:00:00Z"
  },
  {
    "id": "uuid",
    "incident_id": "uuid",
    "event_type": "INCIDENT_UPDATED",
    "message": "Operadora acionada; protocolo DEMO-123.",
    "actor_subject": "demo-operator",
    "occurred_at": "2026-09-13T15:10:00Z"
  }
]
```

Tipos implementados:
- `INCIDENT_CREATED`;
- `INCIDENT_UPDATED`;
- `INCIDENT_NORMALIZED`.

A Sprint 2 não oferece endpoint para editar ou excluir eventos da timeline.

## Autoridade e segurança

- `tenant_id` nunca é aceito do body como autoridade;
- `actor_subject` nunca é aceito do body como autoridade;
- consultas e ações são tenant-scoped;
- campos extras nos payloads de comando são rejeitados;
- queries usam SQLAlchemy parametrizado;
- identidade real/OIDC/RBAC ainda não fazem parte desta alpha.

## Estado de release

Contrato validado por testes de integração e pelo workflow `Sprint 2 Functional Smoke`, exclusivamente em escopo local/teste.
