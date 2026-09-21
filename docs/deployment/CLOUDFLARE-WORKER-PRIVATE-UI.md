# Cloudflare Worker — Private UI Preview

> **Status:** superseded como ambiente ativo pelo
> [Cloudflare Worker + D1 — Private Demo Full-Stack](CLOUDFLARE-WORKER-FULLSTACK-D1.md).
> Este documento preserva o histórico da etapa frontend-only.

## Objetivo original

Publicar o frontend Angular do **P0 — NOC Flow Cloud v2** no Worker existente
`p0-noc-flow-cloud-v2` sem expor uma URL antes de o Cloudflare Access estar ativo.

A etapa foi homologada em 2026-09-21:

- Workers Build verde;
- URL `workers.dev` habilitada somente depois de Access em `All traffic`;
- Angular carregado;
- janela anônima bloqueada.

## Evolução

O preview frontend-only exibia falha em `/api/v1` porque ainda não havia backend
no Worker. O ADR-0009 adiciona um adapter Worker + D1 que preserva o contrato
HTTP necessário para o private demo ser funcional.

O stack canônico FastAPI/PostgreSQL continua preservado e não é substituído pela
decisão de demo.
