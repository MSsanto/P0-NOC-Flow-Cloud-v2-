# Sprint 1 — Security Review

Data: 2026-09-09
Escopo: v0.1.0-alpha, execução local/teste. Referências: OWASP Top 10, OWASP API Security, least privilege, secure by default e defense in depth.

## Resultado

**APROVADA PARA ALPHA LOCAL/TESTE.** Nenhum achado Critical ou High explorável dentro do escopo suportado da Sprint 1. **Não aprovada para exposição pública/produção** enquanto autenticação/autorização real (OIDC e políticas) não substituir o contexto demo.

## Controles verificados

- **Tenant isolation:** `tenant_id` vem do contexto do servidor; payloads extras são rejeitados. Repository filtra tenant em list/detail e testes cobrem isolamento/forja.
- **Fail closed fora de dev/test:** contexto demo só é permitido em `development`/`test`; ambiente não suportado não concede identidade implícita.
- **Input validation:** Pydantic e constraints de banco validam tamanhos, enums, datas e estados. `started_at` futuro retorna 422.
- **SQL injection:** acesso a dados via SQLAlchemy/queries parametrizadas; sem concatenação SQL no vertical slice.
- **CORS:** allowlist configurável por settings; não usa wildcard de credenciais.
- **Errors:** Problem Details evita stack trace para o cliente e preserva `X-Request-ID` para correlação.
- **Dependency security:** CI executa `pip-audit` e `npm audit --audit-level=high`.
- **Containers:** backend roda como usuário não-root; contextos Docker excluem arquivos locais/sensíveis.
- **Web headers:** `nosniff`, `DENY`, Referrer-Policy, Permissions-Policy e CSP restritiva são entregues pelo Nginx.
- **Secrets:** nenhum segredo de produção deve ser versionado. Credenciais padrão do Compose são exclusivamente de desenvolvimento local.

## Achados

### HIGH — Identidade real ainda não implementada (bloqueador de produção)

**Estado:** risco contido no alpha porque o produto não está aprovado para produção e o provider demo falha fora de dev/test.

**Mitigação obrigatória antes de produção:** OIDC, validação de token no backend, autorização tenant-scoped e testes negativos de cross-tenant com identidades reais.

### MEDIUM — Credenciais previsíveis no Compose local

`nocflow/nocflow` é adequado apenas para ambiente descartável/local. Não reutilizar em staging/produção. Secrets deverão vir do mecanismo de configuração/secret store do ambiente.

### LOW — CSP ainda permite `unsafe-inline` em estilos

Necessário no estado atual do Angular por estilos de componentes. Reavaliar nonce/hash e remoção de `unsafe-inline` quando a política de frontend estabilizar.

## Critérios para próxima fase

1. Nenhum deploy público antes da implementação de identidade/autorização.
2. Staging/production devem usar secrets externos e TLS no edge.
3. Manter audits de dependências, testes de tenant e smoke funcional como gates.
4. Reexecutar AppSec quando autenticação, escrita/edição de incidentes ou integrações externas forem adicionadas.
