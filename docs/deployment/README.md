# Deployment

Documentação de execução e ambientes do P0 — NOC Flow Cloud v2.

## Private demo

- [Cloudflare Private Demo](CLOUDFLARE-PRIVATE-DEMO.md) — Docker Compose sem portas públicas, Cloudflare Tunnel e Cloudflare Access deny-by-default.
- [Cloudflare Worker — Private UI Preview](CLOUDFLARE-WORKER-PRIVATE-UI.md) — frontend Angular em Workers Static Assets, sem URL até o Access estar ativo.

## Produção

Produção pública ainda não está autorizada. O roadmap exige identidade confiável (OIDC), RBAC, hardening, observabilidade, estratégia de backup/restore e homologação do ambiente antes de exposição produtiva.
