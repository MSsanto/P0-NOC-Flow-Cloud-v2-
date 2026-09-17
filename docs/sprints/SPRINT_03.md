# Sprint 3 — resumo e evidências

**Incremento:** Auth, RBAC & Multi-Tenancy  
**Estado:** concluído tecnicamente em 15/09/2026; aguardando homologação manual  
**Release candidata:** `v0.3.0-beta`

## Resultado

A Sprint 3 substituiu a identidade puramente sintética por providers explícitos e configuráveis. A demo privada pode confiar em Cloudflare Access ou em um provedor OIDC genérico; o backend resolve a identidade, consulta memberships internas, calcula permissões e mantém o tenant como autoridade server-side.

## Evidências

- commit em `main`: [`12bee12f`](https://github.com/MSsanto/P0-NOC-Flow-Cloud-v2-/commit/12bee12f6cacb2265fbe40306cd88c8bcc6fc2a5);
- migration `20260915_0003_users_memberships.py`;
- módulos `backend/app/modules/tenancy/`;
- endpoint `GET /api/v1/auth/me`;
- providers `demo`, `oidc` e `cloudflare_access`;
- matriz RBAC com Admin, Supervisor, Operator e Viewer;
- testes `test_auth_security.py`, `test_auth_memberships.py` e `test_cloudflare_access_membership.py`;
- stack privada em `compose.private.yaml`.

## Gates automatizados

No commit de integração foram concluídos com sucesso:

- CI principal;
- Sprint 2 Functional Smoke;
- Private Demo Compose.

## Segurança validada

- token OIDC validado por assinatura/JWKS, issuer, audience e claims obrigatórias;
- autorização executada no backend;
- memberships internas determinam tenant e roles;
- acesso sem membership é negado;
- tentativas cross-tenant são cobertas por testes;
- provider demo não é permitido como identidade confiável em ambiente protegido.

## Antes da homologação

A versão continua candidata. Ainda devem ser executados o roteiro manual de 401/403/sessão expirada, a validação visual do fluxo privado e o registro formal da homologação. Produção pública permanece bloqueada.
