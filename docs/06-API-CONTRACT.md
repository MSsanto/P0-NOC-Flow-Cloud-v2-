# Contrato da API v1

Base: `/api/v1`

O OpenAPI gerado pelo FastAPI é a fonte executável do contrato implementado. Este documento registra as convenções estáveis e o estado funcional alcançado até a Sprint 2.

## Convenções

- JSON UTF-8;
- API versionada na URL (`/api/v1`);
- timestamps ISO-8601/UTC;
- erros da aplicação em Problem Details;
- `X-Request-ID` usado para correlação quando aplicável;
- tenant e identidade do ator são autoridade server-side;
- SQL é acessado via SQLAlchemy parametrizado;
- mudanças incompatíveis exigem evolução explícita de contrato/versionamento.

## Health

```text
GET /health/live
GET /health/ready
```

## Incidentes — endpoints implementados

```text
GET  /incidents
POST /incidents
GET  /incidents/query
GET  /incidents/{incident_id}
POST /incidents/{incident_id}/updates
POST /incidents/{incident_id}/normalize
GET  /incidents/{incident_id}/timeline
```

Endpoints de lifecycle adicionais previstos no roadmap (`acknowledge`, `monitor`, `close`, `reopen`) não devem ser considerados implementados até o incremento correspondente.

## Criar incidente

`POST /incidents`

Request:

```json
{
  "title": "Perda de conectividade WAN",
  "affected_resource": "DEMO-SJC-EDGE-01",
  "severity": "CRITICAL",
  "impact_type": "OUTAGE",
  "symptoms": "Perda total de conectividade observada no recurso monitorado.",
  "started_at": "2026-09-13T12:30:00Z"
}
```

Regras:
- `title`: 3–120 caracteres;
- `affected_resource`: 2–120;
- `severity`: `CRITICAL | HIGH | MEDIUM | LOW`;
- `impact_type`: `OUTAGE | DEGRADATION`;
- `symptoms`: 10–2000;
- `started_at`: não pode estar no futuro;
- `tenant_id`, ator, ID, status e timestamps são definidos pelo servidor;
- status inicial: `OPEN`;
- sucesso: `201`.

## Listagem simples

`GET /incidents`

Mantido retrocompatível com a Sprint 1 e retorna um array simples do tenant ativo.

## Consulta avançada

`GET /incidents/query`

Parâmetros:

```text
status        opcional; enum de IncidentStatus
severity      opcional; CRITICAL|HIGH|MEDIUM|LOW
started_from  opcional; datetime ISO-8601
started_to    opcional; datetime ISO-8601
page          >= 1; padrão 1
page_size     1..100; padrão 25
sort          started_at|updated_at; padrão started_at
order         asc|desc; padrão desc
```

`started_from` não pode ser posterior a `started_to`.

Resposta:

```json
{
  "items": [],
  "page": 1,
  "page_size": 25,
  "total": 0
}
```

## Detalhe

`GET /incidents/{incident_id}`

Retorna somente recurso pertencente ao tenant ativo; recurso fora do contexto autorizado é tratado como não encontrado no fluxo suportado.

## Atualização operacional

`POST /incidents/{incident_id}/updates`

```json
{
  "message": "Operadora acionada; protocolo DEMO-123."
}
```

Regras:
- `message`: 3–2000 caracteres;
- ator/timestamp definidos server-side;
- sucesso grava `INCIDENT_UPDATED` e incrementa `version`;
- `RESOLVED`/`CLOSED` rejeitam update com `409`;
- incidente inexistente no tenant ativo retorna `404`;
- campos extras/autoridade forjada retornam `422`.

## Normalização

`POST /incidents/{incident_id}/normalize`

```json
{
  "note": "Conectividade restabelecida e validada."
}
```

`note` é opcional; se fornecida, 3–2000 caracteres.

Regras:
- estado final da operação da Sprint 2: `RESOLVED`;
- grava `INCIDENT_NORMALIZED` e incrementa `version`;
- segunda normalização ou incidente já encerrado retorna `409`;
- ator/timestamp são server-side.

## Timeline

`GET /incidents/{incident_id}/timeline`

Eventos retornados em ordem cronológica:

```text
INCIDENT_CREATED
INCIDENT_UPDATED
INCIDENT_NORMALIZED
```

Shape:

```json
{
  "id": "uuid",
  "incident_id": "uuid",
  "event_type": "INCIDENT_UPDATED",
  "message": "Operadora acionada.",
  "actor_subject": "demo-operator",
  "occurred_at": "2026-09-13T15:00:00Z"
}
```

A API da Sprint 2 não oferece alteração ou exclusão de eventos da timeline.

## Erros principais

- `200/201`: sucesso;
- `400`: requisição malformada quando aplicável;
- `401`: reservado para autenticação real futura;
- `403`: reservado para autorização/RBAC real futura;
- `404`: recurso inexistente no contexto autorizado;
- `409`: conflito de lifecycle;
- `422`: validação estrutural/semântica;
- `500`: erro inesperado, sem exposição de stack/SQL/secrets.

## Segurança e identidade da alpha

Na Sprint 2, tenant e ator são resolvidos por contexto server-side. O provider demo só é suportado em `development/test`. O cliente não controla `tenant_id` ou `actor_subject` por body.

OIDC/RBAC, identidade confiável e exposição pública pertencem a incremento posterior. A `v0.2.0-alpha` não é aprovada para produção.

## Contrato detalhado do incremento

Exemplos adicionais e parâmetros da Sprint 2: [`api/SPRINT_02-INCIDENTS.md`](api/SPRINT_02-INCIDENTS.md).
