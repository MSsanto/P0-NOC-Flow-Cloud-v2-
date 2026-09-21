# ADR-0009 — Adapter Cloudflare Worker + D1 para private demo

## Status

Accepted — 2026-09-21

## Contexto

O backend canônico do NOC Flow Cloud v2 usa FastAPI, SQLAlchemy, Alembic e PostgreSQL.
O private demo precisava ficar funcional no plano gratuito da Cloudflare, sem depender
de Docker local, servidor externo ou exposição pública.

Cloudflare Workers suporta assets estáticos e D1 no plano Free. Wrangler também
suporta provisionamento automático de D1 quando a binding é declarada sem
`database_id`.

## Decisão

Manter FastAPI/PostgreSQL como arquitetura canônica e adicionar um **adapter de
private demo** no Worker existente `p0-noc-flow-cloud-v2`.

O adapter:

- serve o Angular por Workers Static Assets;
- executa `/api/*` no Worker antes dos assets;
- reproduz o contrato REST `/api/v1` usado pelo Angular;
- persiste dados de demo em D1;
- usa `tenant_id` explícito em todas as consultas;
- cria somente um tenant privado de demonstração;
- bootstrapa como Admin apenas a primeira identidade já autorizada pelo Access;
- nega identidades posteriores sem membership;
- exige token Cloudflare Access assinado para a API;
- mantém `preview_urls=false`;
- depende do Cloudflare Access em `All traffic` como primeira camada de controle.

A binding D1 fica declarada como:

```json
{
  "d1_databases": [{ "binding": "DB" }]
}
```

sem ID no Git. O Wrangler provisiona e associa o recurso remoto.

## Fronteira de segurança

O Worker valida a assinatura RS256 do `Cf-Access-Jwt-Assertion` usando os JWKS do
issuer `*.cloudflareaccess.com`, verifica expiração e consistência do e-mail.

O audience não é persistido no repositório público. A autorização primária de
acesso à aplicação permanece no Worker-level Cloudflare Access, que é homologado
separadamente em janela anônima.

RBAC de aplicação continua sendo derivado da membership persistida, não de role
fornecida pelo token externo.

## Compatibilidade

O adapter implementa os endpoints usados pelo frontend atual:

- `GET /api/v1/auth/me`;
- `GET /api/v1/incidents`;
- `GET /api/v1/incidents/query`;
- `POST /api/v1/incidents`;
- `GET /api/v1/incidents/{id}`;
- `POST /api/v1/incidents/{id}/updates`;
- `POST /api/v1/incidents/{id}/normalize`;
- `GET /api/v1/incidents/{id}/timeline`;
- `GET /api/v1/health/live`;
- `GET /api/v1/health/ready`.

## Alternativas consideradas

### Cloudflare Containers

Rejeitado para o private demo atual porque exige plano pago.

### Tunnel para Docker local

Mantido como alternativa e referência para o stack canônico, mas bloqueado no
notebook atual enquanto a virtualização não estiver disponível.

### Migrar o produto inteiro de PostgreSQL para D1

Rejeitado. D1 é uma adaptação de ambiente de demonstração, não uma troca silenciosa
do banco principal.

### Hospedar FastAPI/PostgreSQL em terceiro

Adiado para evitar outra conta, outra superfície operacional e custo/limite externo.

## Consequências

Positivas:

- private demo full-stack pode funcionar no plano Free;
- mesma origem para Angular e API;
- sem CORS entre frontend e backend;
- sem servidor local ligado;
- persistência real para demonstração;
- Access continua bloqueando usuários anônimos.

Trade-offs:

- existe uma implementação de persistência específica de demo;
- D1/SQLite não é idêntico a PostgreSQL;
- o adapter deve acompanhar mudanças futuras do contrato REST;
- não deve receber dados reais de clientes.

## Regra de saída

Uma release pública/produção continua proibida sem a arquitetura de produção,
hardening, observabilidade, backup/restore e homologação formal.
