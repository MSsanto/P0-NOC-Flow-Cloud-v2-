# Contrato da API v1

Base: `/api/v1`

O OpenAPI gerado pelo FastAPI será fonte executável do contrato quando a implementação começar. Este documento define o desenho antes do código e registra as decisões canônicas já refinadas para a Sprint 1.

## Versionamento

- a versão principal faz parte da URL: `/api/v1`;
- mudanças aditivas e retrocompatíveis permanecem em `v1`;
- renomear/remover campos obrigatórios, mudar semântica de status ou alterar payload de forma incompatível exige nova versão principal ou migração explicitamente acordada;
- endpoints em depreciação devem ser documentados no OpenAPI e mantidos durante uma janela definida quando houver consumidores ativos;
- correções de bug que restauram o contrato documentado não criam nova versão;
- o frontend deve consumir somente contratos publicados, sem depender de campos acidentais não documentados.

## Convenções

- JSON em UTF-8;
- timestamps ISO-8601 UTC (`Z`);
- paginação por cursor quando houver grande volume; offset pode ser usado inicialmente em cadastros pequenos;
- erros no formato Problem Details compatível com RFC 9457;
- `X-Request-ID` aceito/gerado e devolvido;
- tenant ativo vem do contexto autorizado, nunca é aceito cegamente do body;
- `Idempotency-Key` será exigida em endpoints de ingestão externa futura.

## Contrato de erros

Todo erro HTTP gerado pela aplicação deve possuir uma representação estável e não expor stack trace, SQL, tokens, secrets ou detalhes internos.

Formato base:

```json
{
  "type": "https://nocflow.example/problems/incident-state-conflict",
  "title": "Incident state conflict",
  "status": 409,
  "detail": "The incident cannot transition from CLOSED to RESOLVED.",
  "instance": "/api/v1/incidents/01J.../resolve",
  "code": "INCIDENT_STATE_CONFLICT",
  "request_id": "01J..."
}
```

Campos:

- `type`: identificador estável da classe do problema;
- `title`: resumo legível e estável;
- `status`: status HTTP;
- `detail`: detalhe seguro para o consumidor;
- `instance`: recurso/operação HTTP relacionada;
- `code`: código de erro estável para tratamento programático;
- `request_id`: correlação com logs e tracing.

Erros de validação podem acrescentar:

```json
{
  "errors": [
    {
      "field": "title",
      "code": "REQUIRED",
      "message": "Field is required."
    }
  ]
}
```

A UI pode traduzir mensagens para o usuário, mas deve usar `code`/`errors[].code` para comportamento programático quando necessário.

## Health

- `GET /health/live`
- `GET /health/ready`

## Sessão/contexto

- `GET /me`
- `GET /me/tenants`
- `POST /me/active-tenant` — somente se adotarmos contexto persistido; alternativa preferida é tenant explícito em header/route validado.

Na Sprint 1, antes da autenticação completa da Sprint 3, tenant e ator podem ser resolvidos por provider de desenvolvimento/demo explicitamente isolado, configurado pelo backend e usando somente dados sintéticos. O cliente não envia `tenant_id` nem identidade como autoridade do body.

## Base operacional

- `GET /sites`
- `POST /sites`
- `GET /sites/{site_id}`
- `PATCH /sites/{site_id}`
- `GET /sites/{site_id}/circuits`
- `POST /circuits`
- `PATCH /circuits/{circuit_id}`
- `GET /carriers`
- `POST /carriers`
- `GET /severities`
- `POST /severities`

Os endpoints de base operacional fazem parte do modelo alvo e não são pré-requisito para o recorte mínimo de incidente da Sprint 1.

## Incidentes

- `GET /incidents`
- `POST /incidents`
- `GET /incidents/{incident_id}`
- `POST /incidents/{incident_id}/acknowledge`
- `POST /incidents/{incident_id}/updates`
- `POST /incidents/{incident_id}/monitor`
- `POST /incidents/{incident_id}/resolve`
- `POST /incidents/{incident_id}/close`
- `POST /incidents/{incident_id}/reopen`
- `GET /incidents/{incident_id}/timeline`
- `POST /incidents/{incident_id}/protocols`

### Sprint 1 — contrato canônico de `POST /incidents`

Request:

```json
{
  "title": "Perda de conectividade WAN",
  "affected_resource": "DEMO-SJC-EDGE-01",
  "severity": "CRITICAL",
  "impact_type": "OUTAGE",
  "symptoms": "Perda total de conectividade observada no recurso monitorado.",
  "started_at": "2026-09-08T12:30:00Z"
}
```

Regras:

- `title`: string, 3–120 caracteres;
- `affected_resource`: string, 2–120 caracteres;
- `severity`: `CRITICAL | HIGH | MEDIUM | LOW`;
- `impact_type`: `OUTAGE | DEGRADATION`;
- `symptoms`: string, 10–2000 caracteres;
- `started_at`: ISO-8601 UTC; não pode ser posterior ao momento do registro;
- `tenant_id`, ator, `id`, `status`, `created_at` e `updated_at` são definidos pelo backend/contexto e não são aceitos como autoridade do body;
- status inicial: `OPEN`;
- request inválido não pode criar registro parcial.

Resposta de sucesso: `201 Created` com o incidente persistido, incluindo no mínimo `id`, os campos recebidos, `status`, `created_at` e `updated_at`.

Para a Sprint 1, validação estrutural/campos inválidos usa `422` no formato Problem Details adotado pela aplicação. Malformação de JSON/requisição pode usar `400`.

`site_id`, `severity_id`, `source` e a base operacional configurável permanecem no modelo alvo e serão introduzidos por evolução explícita de contrato/migration, não como campos ocultos da US-002.

### Exemplo conceitual — atualização

```json
{
  "occurred_at": "2026-09-08T12:45:00Z",
  "situation": "Circuito permanece indisponível",
  "action_taken": "Chamado aberto com operadora",
  "next_action": "Aguardar diagnóstico da operadora"
}
```

### Exemplo conceitual — resolução

```json
{
  "resolved_at": "2026-09-08T13:20:00Z",
  "resolution": "Conectividade restabelecida e validada",
  "corrective_action": "Energia elétrica restabelecida na localidade"
}
```

## Templates/comunicação

- `GET /templates`
- `POST /templates`
- `POST /templates/{template_id}/versions`
- `POST /incidents/{incident_id}/communications/render`
- `GET /incidents/{incident_id}/communications`

Renderizar não envia comunicação. Envio externo é P4 e sempre terá política explícita.

## Passagem de turno

- `POST /handovers/preview`
- `POST /handovers`
- `GET /handovers`
- `GET /handovers/{handover_id}`
- `POST /handovers/{handover_id}/finalize`

## Auditoria

- `GET /audit-events` — restrito a papéis autorizados.

## Filtros principais de incidentes

`status`, `severity`, `site`, `carrier`, `protocol`, `detected_from`, `detected_to`, `query`, `cursor`, `limit`.

Filtros que dependem de `site`, `carrier` e demais entidades de base operacional entram somente quando essas entidades existirem no incremento correspondente. A Sprint 1 deve implementar apenas os filtros aprovados em suas histórias.

## Códigos esperados

- `200/201/204`: sucesso;
- `400`: contrato inválido/requisição malformada quando aplicável;
- `401`: não autenticado;
- `403`: sem autorização no tenant/recurso;
- `404`: recurso inexistente no contexto autorizado;
- `409`: conflito de estado/versão/duplicidade;
- `422`: validação semântica/estrutural da entrada conforme contrato FastAPI;
- `429`: rate limit futuro;
- `500`: erro inesperado com request ID.

## Regra de segurança

Para reduzir enumeração cross-tenant, recursos que existem em outro tenant devem ser tratados como não encontrados para usuários sem acesso, salvo necessidade administrativa explicitamente autorizada.
