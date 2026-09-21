# Cloudflare Worker — Private UI Preview

## Objetivo

Publicar o frontend Angular do **P0 — NOC Flow Cloud v2** no Worker existente
`p0-noc-flow-cloud-v2` sem expor uma URL antes de o Cloudflare Access estar ativo.

Este fluxo é um **preview privado da interface**. Ele não substitui o private demo
full-stack baseado em Tunnel + FastAPI + PostgreSQL.

## Estado seguro inicial

O arquivo `apps/web/wrangler.jsonc` mantém:

```json
{
  "workers_dev": false,
  "preview_urls": false
}
```

Isso permite validar build/deploy do Worker sem criar uma URL pública.

## Configuração do Workers Builds

No Worker existente, em **Settings > Build**, usar:

- Root directory: `apps/web`
- Build command: `npm install --global npm@11 && npm ci && npm run build`
- Deploy command: `npx wrangler deploy`

O runtime do build é fixado por `apps/web/.node-version`.

## Ordem de ativação privada

1. Fazer um build com `workers_dev=false` e confirmar sucesso.
2. Abrir a aba **Access** do Worker.
3. Selecionar **Protect this Worker behind Access**.
4. Proteger **All traffic**.
5. Restringir a política à identidade autorizada.
6. Somente depois habilitar a URL `workers.dev`.
7. Atualizar `workers_dev` para `true` no repositório e redeployar.
8. Confirmar em janela anônima que o login do Access aparece antes da aplicação.

Nunca habilitar `workers.dev` antes da política Access.

## SPA

O Angular gera os assets em:

```text
dist/noc-flow-cloud-web/browser
```

O Worker usa `not_found_handling = single-page-application`, portanto rotas
client-side do Angular retornam `index.html` em navegações que não correspondem
a um arquivo estático.

## Limitação atual

O frontend de produção usa `/api/v1`. Nesta etapa a Cloudflare hospeda apenas os
assets Angular; portanto chamadas à API não estarão funcionais até conectar o
backend FastAPI/PostgreSQL ao front door privado.

A versão full-stack continua documentada em
`docs/deployment/CLOUDFLARE-PRIVATE-DEMO.md`.

## Gate

- Angular type-check: PASS;
- testes unitários: PASS;
- build de produção: PASS;
- `index.html` presente no diretório de assets;
- configuração Wrangler com SPA fallback;
- `workers_dev=false`;
- `preview_urls=false`;
- `wrangler deploy --dry-run`: PASS;
- Access ativo antes de qualquer URL.
