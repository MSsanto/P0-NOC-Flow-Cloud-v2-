# ADR-0009 — Auditoria persistida e observabilidade provider-neutral

**Status:** Accepted  
**Data:** 2026-09-21

## Contexto

O sistema já possui request ID e health checks, mas ainda não possui trilha de auditoria persistida nem logging estruturado por request. A solução precisa melhorar rastreabilidade sem antecipar Azure nem registrar conteúdo operacional sensível.

## Decisão

1. Persistir `audit_events` em PostgreSQL, append-only no contrato HTTP.
2. Auditar somente metadados allowlisted.
3. Gravar auditoria de mutações críticas na mesma transação da mudança.
4. Usar `X-Request-ID` sanitizado como correlação HTTP → log → auditoria.
5. Emitir logs JSON via biblioteca padrão de Python.
6. Nunca logar body, Authorization ou Cookie.
7. Manter `/health/live` e `/health/ready` separados.
8. Adiar OpenTelemetry/Application Insights real para a etapa cloud.

## Consequências

- investigação reproduzível;
- menor risco de vazamento;
- nova migration/tabela;
- repositories críticos passam a registrar audit event antes do commit;
- retenção precisa ser definida antes de produção.

## Rejeitado

- auditoria somente em arquivo/log;
- body logging;
- SDK Azure no domínio;
- microserviço separado de auditoria.
