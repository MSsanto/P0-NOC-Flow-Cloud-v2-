# Observabilidade

## Objetivos

Responder rapidamente:

- a API está saudável?
- qual endpoint está falhando?
- qual request produziu o erro?
- há degradação de latência?
- um tenant específico está enfrentando erro sem expor seus dados?
- uma integração externa está instável?

## Logs estruturados

Campos mínimos:

- timestamp UTC;
- level;
- service;
- environment;
- request_id;
- trace_id quando disponível;
- route;
- method;
- status_code;
- duration_ms;
- actor_id pseudonimizado/ID interno quando necessário;
- tenant_id interno quando necessário e permitido;
- error_code.

Não registrar tokens, secrets, senhas, bodies completos por padrão, CNPJ/telefone/contato ou texto operacional desnecessário.

## Métricas

- requests por endpoint/status;
- latência p50/p95/p99;
- error rate;
- DB connection pool;
- incident creations/updates/resolutions como métricas agregadas do sistema, sem dados sensíveis;
- falhas de integração;
- filas futuras.

## Tracing

OpenTelemetry é opção preferencial para instrumentação vendor-neutral. Exportação pode apontar para Application Insights.

## Health

### `/health/live`
Processo está vivo. Não deve depender de serviços externos lentos.

### `/health/ready`
API está pronta para servir requests; pode validar dependências essenciais como banco.

## Alertas de plataforma

Quando P3 existir:

- aumento de 5xx;
- readiness falhando;
- latência acima da meta;
- banco indisponível;
- falha repetida de deployment;
- consumo anormal de recursos.

## Auditoria ≠ log técnico

Audit log registra ações de negócio/governança e possui retenção/política própria. Logs técnicos servem diagnóstico e não substituem auditoria.