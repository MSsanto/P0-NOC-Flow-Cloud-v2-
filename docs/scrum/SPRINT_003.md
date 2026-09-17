# Sprint 003 — Auth, RBAC & Multi-Tenancy

**Status:** Concluída tecnicamente em 15/09/2026; candidata à homologação  
**Duração planejada:** 2 semanas  
**Release alvo:** `v0.3.0-beta`  
**Sprint Goal:** implementar identidade, autorização server-side e isolamento seguro entre tenants.

## User Stories

### US-008 — Autenticar usuário [P0]
Como usuário autorizado, quero entrar no NOC Flow Cloud com minha identidade corporativa para acessar o sistema de forma segura.

**Responsável primário:** 05 Backend & API  
**Dependências:** 02 Architecture, 09 Security, 04 Frontend.

### US-009 — Aplicar RBAC [P0]
Como administrador, quero que cada perfil possua somente as ações necessárias para reduzir risco operacional.

**Responsável primário:** 05 Backend & API

Perfis iniciais candidatos: Admin, Supervisor, Operator, Viewer.

### US-010 — Isolar tenants [P0]
Como responsável por uma operação, quero que dados de outro tenant nunca sejam expostos para preservar confidencialidade e integridade.

**Responsável primário:** 05 Backend & API  
**Dependências:** 06 Database, 09 Security.

## Distribuição por especialistas

- **01 PO:** validar matriz de permissões.
- **02 Architecture:** OIDC/OAuth2, tenant context e boundaries.
- **03 UX/UI:** login, sessão expirada, acesso negado e troca/contexto de tenant quando aplicável.
- **04 Frontend:** auth flow, guards e estados 401/403.
- **05 Backend:** token validation, RBAC e tenant scoping.
- **06 Database:** membership/tenant e constraints.
- **07 QA:** auth, roles e cross-tenant.
- **08 DevOps:** configuração de identidade por ambiente e secrets.
- **09 Security:** threat model específico, IDOR/BOLA, privilege escalation, token validation.
- **10 Docs:** security/auth/API docs.
- **11 Review:** review independente.
- **12 Release:** homologação `v0.3.0-beta`.

## Tasks principais

TASK-PO-S3-01 matriz RBAC; TASK-ARC-S3-01 OIDC/tenant context; TASK-UX-S3-01 login/401/403; TASK-DB-S3-01 memberships; TASK-BE-S3-01 token validation; TASK-BE-S3-02 authorization; TASK-BE-S3-03 tenant scoping; TASK-FE-S3-01 auth integration; TASK-FE-S3-02 guards; TASK-QA-S3-01 roles; TASK-QA-S3-02 cross-tenant; TASK-SEC-S3-01 BOLA/IDOR/privilege escalation; TASK-DO-S3-01 secrets/config; TASK-DOC-S3-01 docs; TASK-CR-S3-01 review; TASK-REL-S3-01 homologação.

## Critérios de sucesso

- identidade confiável determinada pelo backend;
- autorização não depende do frontend;
- nenhum acesso cross-tenant permitido;
- 401/403 tratados corretamente;
- testes negativos de segurança verdes;
- release homologada.


## Evidência de implementação

Commit de integração em `main`: `12bee12f6cacb2265fbe40306cd88c8bcc6fc2a5`.

Entregas verificadas:

- provider local sintético restrito a `development`/`test`;
- validação OIDC/JWT genérica com JWKS, issuer e audience;
- integração com Cloudflare Access para demo privada;
- endpoint `GET /api/v1/auth/me`;
- perfis Admin, Supervisor, Operator e Viewer;
- autorização server-side por permission;
- usuários e memberships persistidos por Alembic;
- isolamento cross-tenant e testes negativos;
- contexto de autenticação consumido pelo Angular;
- stack privada validada por `compose.private.yaml`.

Gates verdes no commit de integração:

- `CI`;
- `Sprint 2 Functional Smoke`;
- `Private Demo Compose`.

## Pendências de homologação

- executar roteiro manual de 401, 403 e sessão expirada no ambiente privado;
- registrar evidência visual da experiência de acesso;
- atualizar a versão/tag somente após homologação;
- manter deploy público bloqueado até o hardening da Sprint 6.
