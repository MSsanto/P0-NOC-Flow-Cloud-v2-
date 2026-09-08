# ADR-0003 — Incidente como agregado com timeline append-only

**Status:** Accepted  
**Data:** 2026-09-08

## Contexto

A versão anterior trata alerta, atualização e normalização como etapas visíveis. Na cloud multiusuário, precisamos preservar histórico, concorrência e integração.

## Decisão

Modelar um `Incident` como agregado principal. Alerta inicial, updates, mudança de status, protocolos, normalização e reabertura geram eventos de timeline append-only.

Estados iniciais:

`OPEN → ACKNOWLEDGED → INVESTIGATING → MONITORING → RESOLVED → CLOSED`, com reabertura autorizada para `INVESTIGATING`.

## Consequências

- histórico não é perdido quando o estado atual muda;
- handover e auditoria podem referenciar fatos no tempo;
- integrações conseguem mapear eventos;
- UI mantém linguagem operacional sem forçar modelo de tabelas separado para cada etapa.

## Correções

Um evento histórico não deve ser apagado/regravado para esconder erro. Correções relevantes geram novo evento, preservando autoria e contexto.