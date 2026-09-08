# Sprint 1 — Security Baseline

Status: **EM ANDAMENTO — design review concluído; validação de implementação pendente**  
Owner: **09 Security & AppSec**  
Referências: OWASP Top 10, OWASP API Security Top 10, least privilege, secure by default e defense in depth.

## Escopo

Este baseline cobre o primeiro vertical slice do NOC Flow Cloud v2: listagem, criação e detalhe de incidentes, fundação FastAPI/Angular/PostgreSQL, Docker/CI e preparação para multi-tenancy.

O repositório ainda está em fase de fundação. Portanto, esta revisão diferencia:

- controles já definidos em arquitetura/documentação;
- controles verificáveis no repositório atual;
- controles que só poderão ser aprovados quando houver implementação.

Nenhum item documentado abaixo deve ser interpretado como validação de código ainda inexistente.

## Trust boundaries e ativos

### Ativos prioritários

1. incidentes e timelines;
2. identidade do usuário e memberships;
3. tenant e contexto ativo;
4. tokens OIDC/OAuth2;
5. segredos de banco, Azure, GitHub e integrações;
6. trilha de auditoria;
7. dados operacionais e exports;
8. logs e telemetry.

### Fronteiras de confiança

```text
Browser Angular
   |
   | HTTPS
   v
FastAPI / API v1
   |
   +--> OIDC Provider
   |
   +--> PostgreSQL
   |
   +--> Logs / Metrics / Tracing
   |
   +--> Integrações externas futuras
```

O browser é sempre tratado como não confiável. Autorização, tenant, transições de estado e regras de integridade devem ser revalidados no backend.

## Threat model inicial

| ID | Severidade | Ameaça | Cenário ofensivo | Mitigação obrigatória |
|---|---|---|---|---|
| SEC-001 | **High** | BOLA / vazamento cross-tenant | usuário altera `incident_id`, `site_id` ou outro identificador e acessa recurso de outro tenant | resolver tenant a partir de identidade/contexto autorizado; repositories sempre tenant-scoped; testes negativos cross-tenant; responder 404 quando recurso não existir no contexto autorizado |
| SEC-002 | **High** | Tenant spoofing | cliente envia `tenant_id` no body/header e força acesso a outra operação | nunca confiar em `tenant_id` fornecido pelo cliente sem validar membership; objetos criados recebem tenant server-side |
| SEC-003 | **High** | Broken Function Level Authorization | usuário comum acessa função administrativa ou transição privilegiada | autorização server-side por permission; 403 consistente; frontend apenas reflete permissão |
| SEC-004 | **High** | Exposição de secrets | `.env`, connection string, token GitHub/Azure ou chave privada é commitada/logada | `.gitignore`; secret store; Managed Identity/Key Vault no Azure; secret scanning no CI; rotação imediata se houver vazamento |
| SEC-005 | **Medium** | CORS permissivo | API aceita qualquer origin ou combina `*` com credenciais | allowlist por ambiente; methods/headers mínimos; `allow_credentials` somente quando necessário; nunca `*` com credenciais |
| SEC-006 | **Medium** | SQL/command injection | parâmetros de filtros/IDs chegam a SQL montado por string | SQLAlchemy/queries parametrizadas; nenhuma interpolação SQL com input; validação Pydantic |
| SEC-007 | **Medium** | Stored/Reflected XSS | campos livres de incidentes/timeline/templates retornam conteúdo malicioso | escaping padrão Angular; não usar bypass de sanitização sem review; CSP quando hospedagem permitir; sanitizar HTML se um requisito futuro realmente permitir HTML |
| SEC-008 | **Medium** | Mass assignment / excessive data exposure | cliente tenta definir `tenant_id`, `created_by`, status, owner ou timestamps | DTOs de entrada separados dos modelos de persistência; campos de sistema nunca aceitos em payload; response models explícitos |
| SEC-009 | **Medium** | Error leakage | stack trace, SQL, connection string ou token aparece em resposta/log | Problem Details; mensagem pública genérica em 500; `request_id`; stack trace somente em ambiente controlado; redaction de secrets |
| SEC-010 | **Medium** | Supply-chain compromise | dependência vulnerável ou workflow inseguro entra no build | versões pinadas/lockfiles; dependency scanning; secret scanning; SAST mínimo; permissions mínimas em GitHub Actions |
| SEC-011 | **Medium** | API abuse / resource exhaustion | listagens, filtros ou writes são chamados em volume excessivo | paginação e limites máximos; timeouts; rate limiting antes de exposição pública; limites de payload |
| SEC-012 | **Low** | Enumeração de IDs | diferença entre 403/404 revela recursos de outro tenant | para recursos fora do tenant autorizado, preferir 404 conforme contrato da API |

## TASK-SEC-001 — Threat model inicial

**Status: CONCLUÍDO NO NÍVEL DE DESIGN.**

Riscos principais identificados: cross-tenant leakage, BOLA/IDOR, tenant spoofing, escalada de privilégio, secret exposure, injection/XSS, excess data exposure, logging inseguro e supply chain.

Validação de implementação deve ocorrer assim que os endpoints FastAPI existirem.

## TASK-SEC-002 — CORS / configuração segura

**Status: REQUISITO DEFINIDO; IMPLEMENTAÇÃO PENDENTE DO BACKEND.**

Baseline obrigatório:

- development: somente origins locais explicitamente necessárias;
- test/staging/production: allowlist explícita por ambiente;
- proibir `allow_origins=["*"]` em ambiente com autenticação/credenciais;
- permitir somente métodos e headers realmente necessários;
- não habilitar credentials por padrão;
- configuração carregada por settings/env, nunca hardcoded para produção;
- teste automatizado verificando origin permitido e origin negado.

Gate: configuração permissiva de CORS em staging/production é **High** e bloqueia release.

## TASK-SEC-003 — Secrets e `.env`

**Status: PARCIALMENTE CONCLUÍDO.**

Verificado no repositório:

- `.env` e `.env.*` estão ignorados;
- `.env.example` é explicitamente permitido;
- `*.pem` e `*.key` estão ignorados;
- dumps/backups e arquivos locais de banco estão ignorados;
- `SECURITY.md` proíbe credenciais e dados operacionais reais.

Pendências para DevOps/CI:

- secret scanning automático;
- dependency scanning Python/Node;
- permissions mínimas do `GITHUB_TOKEN` em workflows;
- Azure preferindo OIDC/Managed Identity em vez de secrets de longa duração;
- Key Vault para segredos quando Azure entrar na Sprint 6.

Gate: qualquer secret real versionado deve ser tratado como comprometido e rotacionado; remover o arquivo do commit atual não é mitigação suficiente.

## TASK-SEC-004 — Riscos de tenant isolation

**Status: DESIGN ACEITÁVEL; IMPLEMENTAÇÃO PENDENTE.**

Controles obrigatórios:

1. `tenant_id` obrigatório nas entidades tenant-scoped;
2. tenant resolvido server-side a partir de identidade + membership/contexto autorizado;
3. repositories recebem tenant explicitamente e filtram por ele em toda query;
4. criação de recurso define tenant server-side;
5. FKs/constraints compostas devem impedir associação acidental entre entidades de tenants distintos quando aplicável;
6. testes negativos devem tentar acessar, atualizar e relacionar IDs de outro tenant;
7. auditoria inclui tenant e ator;
8. PostgreSQL RLS pode ser adotado como defesa adicional após o desenho principal estar correto.

Risco residual atual: a autenticação/RBAC está planejada para Sprint 3, mas as histórias da Sprint 1 já exigem tenant isolation. Até a identidade real existir, qualquer demo deve usar somente contexto sintético controlado pelo backend e não deve ser tratada como pronta para produção.

## TASK-SEC-005 — Revisão OWASP API

**Status: CONCLUÍDO NO NÍVEL DE CONTRATO; CODE REVIEW PENDENTE.**

### Mapeamento prioritário

- API1 BOLA: incidentes, sites, circuits, handovers, audit events;
- API2 Broken Authentication: Sprint 3, OIDC/OAuth2, validação de token no backend;
- API3 Broken Object Property Level Authorization: DTOs explícitos, evitar mass assignment/excesso de campos;
- API4 Unrestricted Resource Consumption: paginação, limites, timeouts e rate limiting;
- API5 Broken Function Level Authorization: RBAC/permissions server-side;
- API6 Unrestricted Access to Sensitive Business Flows: transições de incidente e handover finalization devem validar estado e permissão;
- API7 SSRF: atenção futura a webhooks, URLs de protocolos e integrations/adapters;
- API8 Security Misconfiguration: CORS, debug, OpenAPI exposure, headers e environment settings;
- API9 Improper Inventory Management: `/api/v1`, endpoints documentados e remoção/depreciação controlada;
- API10 Unsafe Consumption of APIs: adapters futuros devem validar TLS, timeouts, schema e respostas externas.

## Requisitos de implementação para Sprint 1

### Backend

- Pydantic com limites de tamanho e enums;
- `tenant_id`, `created_by`, IDs/timestamps e status inicial definidos server-side;
- SQLAlchemy/queries parametrizadas;
- response models explícitos;
- 404 para recurso fora do contexto autorizado;
- erros 500 sem detalhes internos;
- logging sem body sensível, token ou secret;
- limites máximos para `limit`, filtros e payloads.

### Frontend

- confiar no Angular escaping padrão;
- não renderizar conteúdo operacional com `innerHTML` sem justificativa e review;
- não armazenar secrets no bundle/environment;
- erros de API não devem expor detalhes internos;
- authorization UI não substitui authorization backend.

### Database

- tenant scoping obrigatório;
- constraints e índices coerentes com tenant;
- usuário da aplicação sem privilégios administrativos;
- migrations versionadas e revisadas;
- nenhum seed público com dado real.

### CI/CD

Fluxo mínimo esperado:

```text
lint -> unit/integration tests -> dependency scan -> secret scan -> build
```

Antes de staging/production adicionar container scan e gates de release.

## Casos de teste AppSec mínimos

1. criar incidente ignorando `tenant_id` malicioso enviado pelo cliente;
2. consultar `incident_id` de outro tenant retorna 404;
3. atualizar recurso de outro tenant é bloqueado;
4. filtros com payloads de injection não alteram query;
5. textos com `<script>` são tratados como dados, não executados;
6. payload com campos server-managed extras é rejeitado/ignorado conforme contrato explícito;
7. origin não permitido falha em CORS;
8. stack trace e connection string não aparecem em resposta 500;
9. paginação rejeita limites excessivos;
10. logs não contêm Authorization header/token.

## Gate AppSec atual

**APPSEC APPROVED WITH FINDINGS — somente para o desenho/fundação.**

Não existem vulnerabilidades Critical confirmadas no estado atual do repositório porque ainda não há implementação do backend/frontend da Sprint 1 para explorar. Entretanto, controles High relevantes ainda são **pendentes de implementação**, especialmente tenant isolation, autorização e secret scanning.

A Sprint 1 não deve receber aprovação final de release enquanto:

- os endpoints reais não forem submetidos aos testes negativos cross-tenant;
- CORS/configuração não forem verificados em código;
- CI não executar security checks mínimos;
- não houver evidência de que payloads não controlam tenant/autor/status;
- nenhum Critical/High conhecido permanecer sem mitigação definida.

## Próxima revisão obrigatória

Executar AppSec novamente após a primeira implementação funcional de:

- `GET /api/v1/incidents`;
- `POST /api/v1/incidents`;
- `GET /api/v1/incidents/{incident_id}`;
- settings/CORS;
- SQLAlchemy repositories;
- workflow GitHub Actions.
