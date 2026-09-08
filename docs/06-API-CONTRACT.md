# Contrato da API v1

Base: `/api/v1`

O OpenAPI gerado pelo FastAPI será fonte executável do contrato quando a implementação começar. Este documento define o desenho antes do código.

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
      "field": "summary",
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

### Exemplo conceitual — criar incidente

```json
{
  "site_id": "01J...",
  "severity_id": "01J...",
  "source": "manual",
  "detected_at": "2026-09-08T12:30:00Z",
  "summary": "Perda de conectividade WAN detectada"
}
```

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

## Códigos esperados

- `200/201/204`: sucesso;
- `400`: contrato inválido/requisição malformada;
- `401`: não autenticado;
- `403`: sem autorização no tenant/recurso;
- `404`: recurso inexistente no contexto autorizado;
- `409`: conflito de estado/versão/duplicidade;
- `422`: validação semântica;
- `429`: rate limit futuro;
- `500`: erro inesperado com request ID.

## Regra de segurança

Para reduzir enumeração cross-tenant, recursos que existem em outro tenant devem ser tratados como não encontrados para usuários sem acesso, salvo necessidade administrativa explicitamente autorizada.
