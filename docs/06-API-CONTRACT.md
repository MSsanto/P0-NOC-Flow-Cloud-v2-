# Contrato da API v1

Base: `/api/v1`

O OpenAPI gerado pelo FastAPI é a fonte executável do contrato implementado. Este documento registra as convenções estáveis e o estado funcional alcançado até a Sprint 3.

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

## Identidade — endpoint implementado

```text
GET /auth/me
```

`GET /auth/me` retorna o contexto autenticado resolvido pelo backend para o tenant ativo, incluindo identidade e permissões derivadas da membership interna. O cliente não define role ou permissões.

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
- `401`: autenticação ausente, inválida ou expirada;
- `403`: identidade autenticada sem membership ativa ou sem permissão para a ação;
- `404`: recurso inexistente no contexto autorizado;
- `409`: conflito de lifecycle;
- `422`: validação estrutural/semântica;
- `500`: erro inesperado, sem exposição de stack/SQL/secrets.

## Segurança e identidade

Desde a Sprint 3, a API suporta três modos explícitos de identidade:

- `demo`: somente para `development`/`test`;
- `cloudflare_access`: valida o JWT do Cloudflare Access para a demo privada;
- `oidc`: valida bearer token OIDC/JWT por assinatura/JWKS, issuer, audience, expiração e subject.

A autenticação externa identifica o usuário, mas não concede role. O backend resolve `users` e `tenant_memberships` internamente e deriva as permissões a partir da role persistida.

O cliente não controla `tenant_id`, `actor_subject`, roles ou permissões por body. Identidade autenticada sem membership válida recebe `403`; token ausente/inválido recebe `401`.

A candidata `v0.3.0-beta` permanece destinada a ambiente local e demo privada protegida. Produção pública continua bloqueada até homologação e hardening posteriores.

## Contrato detalhado do incremento

Exemplos adicionais e parâmetros da Sprint 2: [`api/SPRINT_02-INCIDENTS.md`](api/SPRINT_02-INCIDENTS.md).


## Contratos planejados da Sprint 4 — ainda não implementados

Os endpoints abaixo são contrato de readiness. Eles não devem ser anunciados como implementados até o merge do incremento correspondente e atualização desta seção.

### Dashboard operacional

`GET /dashboard/summary`

Permissão: `incident:read`.

Resposta alvo:

```json
{
  "active_count": 0,
  "critical_active_count": 0,
  "resolved_in_shift_count": 0,
  "shift": {
    "window_start": "2026-09-21T06:00:00Z",
    "window_end": "2026-09-21T18:00:00Z"
  },
  "items": []
}
```

Regras:

- tenant é resolvido server-side;
- `active_count`: incidentes cujo status não é `RESOLVED` nem `CLOSED`;
- `critical_active_count`: subconjunto ativo com severidade `CRITICAL`;
- `resolved_in_shift_count`: incidentes com `INCIDENT_NORMALIZED` dentro da janela atual;
- fila `items` ordenada por severidade (`CRITICAL > HIGH > MEDIUM > LOW`) e, dentro da mesma severidade, `started_at` ascendente;
- a Sprint 4 não introduz SLA/“aguardando terceiro”/“sem atualização na meta” enquanto essas regras não existirem no domínio.

### Preview de handover

`GET /handovers/preview`

Permissão: `handover:read`.

Resposta alvo:

```json
{
  "window_start": "2026-09-21T06:00:00Z",
  "window_end": "2026-09-21T18:00:00Z",
  "generated_at": "2026-09-21T17:00:00Z",
  "items": []
}
```

O preview é calculado server-side e não persiste draft.

Seleção:

- incidentes ativos no momento da consulta;
- incidentes com `INCIDENT_NORMALIZED` ocorrido dentro da janela do turno;
- união sem duplicidade por incidente.

### Finalizar handover

`POST /handovers`

Permissão: `handover:finalize`.

Request:

```json
{
  "observations": "Pendências do próximo plantão."
}
```

Regras:

- `observations`: opcional; máximo 4000 caracteres; se presente e não vazio, mínimo 3;
- tenant, ator, janela, versão, timestamps e itens são definidos pelo servidor;
- a API recalcula o snapshot no instante da finalização; não aceita lista de incidentes enviada pelo cliente;
- cria handover + itens em uma transação;
- sucesso retorna `201`;
- colisão de versão concorrente retorna `409` com código estável `HANDOVER_VERSION_CONFLICT`;
- ausência de `handover:finalize` retorna `403`;
- campos extras que tentem forjar tenant, ator, versão ou itens retornam `422`.

### Handover mais recente

`GET /handovers/latest`

Permissão: `handover:read`.

- retorna o handover finalizado mais recente do tenant ativo;
- quando não existir handover, retorna `404` com código estável `HANDOVER_NOT_FOUND`.

### Consultar handover

`GET /handovers/{handover_id}`

Permissão: `handover:read`.

- retorna snapshot persistido e seus itens;
- recurso fora do tenant autorizado é tratado como não encontrado;
- versões antigas permanecem consultáveis pelo próprio ID;
- não existem endpoints `PATCH`, `PUT` ou `DELETE` para handover finalizado na Sprint 4.

### Shape alvo do handover

```json
{
  "id": "uuid",
  "version": 1,
  "window_start": "2026-09-21T06:00:00Z",
  "window_end": "2026-09-21T18:00:00Z",
  "observations": "Pendências do próximo plantão.",
  "finalized_by_subject": "operator-subject",
  "finalized_at": "2026-09-21T17:00:00Z",
  "items": [
    {
      "incident_id": "uuid",
      "title": "Perda WAN",
      "affected_resource": "DEMO-EDGE-01",
      "severity": "HIGH",
      "status": "OPEN",
      "started_at": "2026-09-21T14:00:00Z",
      "last_event_message": "Operadora acionada.",
      "last_event_at": "2026-09-21T16:30:00Z"
    }
  ]
}
```

O response não expõe `tenant_id` como dado necessário ao consumidor comum.
