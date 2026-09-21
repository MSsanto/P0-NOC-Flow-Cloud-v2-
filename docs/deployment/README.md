# Deployment

Documentação de execução e ambientes do P0 — NOC Flow Cloud v2.

## Private demo

- [Cloudflare Worker + D1 — Private Demo Full-Stack](CLOUDFLARE-WORKER-FULLSTACK-D1.md) — ambiente privado no plano Free, Angular + API adapter + D1, protegido por Cloudflare Access.
- [Cloudflare Private Demo](CLOUDFLARE-PRIVATE-DEMO.md) — alternativa canônica com Docker Compose, FastAPI, PostgreSQL, Tunnel e Access.
- [Cloudflare Worker — Private UI Preview](CLOUDFLARE-WORKER-PRIVATE-UI.md) — etapa histórica de frontend-only que antecedeu o adapter D1.

## Produção

Produção pública ainda não está autorizada. O roadmap exige identidade confiável, RBAC, hardening, observabilidade, estratégia de backup/restore e homologação formal do ambiente antes de exposição produtiva.
