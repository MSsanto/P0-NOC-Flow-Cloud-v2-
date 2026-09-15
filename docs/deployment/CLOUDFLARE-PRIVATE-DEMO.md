# Cloudflare Private Demo — NOC Flow Cloud v2

## Objetivo

Disponibilizar o NOC Flow Cloud v2 remotamente para demonstração **sem publicar a aplicação na Internet** e sem tratar o ambiente como produção.

O modo autenticado usa:

- Docker Compose;
- `cloudflared` como conexão de saída;
- Cloudflare Tunnel;
- Cloudflare One Client no dispositivo autorizado;
- hostname privado `nocflow.internal`;
- Cloudflare Access para autenticação e política de entrada;
- JWT de Access validado novamente pelo FastAPI;
- `users` e `tenant_memberships` internos como autoridade de tenant/role;
- dados exclusivamente sintéticos.

Cloudflare Tunnel é outbound-only. Nenhuma porta de entrada do host precisa ser aberta.

## Limite de segurança

Este ambiente é **private demo/staging, não produção**.

O modo `demo` continua permitido somente em `development`/`test`. O private demo autenticado deve usar:

```text
NOCFLOW_ENVIRONMENT=staging
NOCFLOW_AUTH_MODE=cloudflare_access
```

Produção pública continua sujeita aos gates de release, segurança e homologação do projeto.

## Arquitetura autenticada

```text
Notebook autorizado
       |
Cloudflare One Client
       |
Cloudflare Access
  login + policy
       |
Cloudflare Tunnel
       |
cloudflared (Docker)
       |
       v
nocflow.internal -> web :80 (Nginx)
                         |
                         | Cf-Access-Jwt-Assertion
                         v
                    backend :8000
                         |
                  valida JWT Access
                  issuer + AUD + JWKS
                         |
                  membership interna
                         |
                         v
                    PostgreSQL :5432
```

O browser não armazena senha do NOC Flow nem Bearer token em `localStorage`. A autenticação acontece no Cloudflare Access antes de a aplicação ser utilizada.

O backend não confia somente no fato de o request ter atravessado a Cloudflare. Ele valida assinatura, issuer, audience e validade do JWT `Cf-Access-Jwt-Assertion` usando as chaves públicas da organização em:

```text
https://<team>.cloudflareaccess.com/cdn-cgi/access/certs
```

Depois da validação externa, a autorização continua interna:

```text
Cloudflare identity (sub)
        |
        v
users.external_subject
        |
        v
tenant_memberships
        |
        +-- tenant
        +-- role: Admin | Supervisor | Operator | Viewer
```

Claims externos não concedem role.

## Preparação local

Copie `.env.example` para um arquivo ignorado pelo Git:

```powershell
Copy-Item .env.example .env.private
```

Gere uma senha forte para `POSTGRES_PASSWORD` e adicione o token do Tunnel somente no arquivo local.

Nunca cole ou versione:

- `CLOUDFLARE_TUNNEL_TOKEN`;
- cookies `CF_Authorization`;
- JWT `Cf-Access-Jwt-Assertion`;
- tokens OIDC;
- senhas.

## 1. Configurar o Tunnel privado

No dashboard Cloudflare:

1. `Networking` → `Tunnels`;
2. criar ou reutilizar `noc-flow-private-demo`;
3. adicionar `Private hostname` para `nocflow.internal`;
4. garantir que o Tunnel alcança o serviço web do Compose;
5. manter a aplicação sem DNS público.

O Cloudflare One Client precisa encaminhar DNS/tráfego desse hostname pela organização Zero Trust.

## 2. Criar a aplicação Access

No dashboard:

1. `Zero Trust` → `Access controls` → `Applications`;
2. `Create new application`;
3. selecionar `Self-hosted and private`;
4. selecionar `Add private hostname`;
5. hostname: `nocflow.internal`;
6. porta: `80`;
7. criar uma política `Allow` somente para a identidade autorizada;
8. não usar `Everyone` nem `Bypass`.

Cloudflare Access suporta fluxo de login em browser para aplicações privadas HTTP na porta 80.

## 3. Identity Provider

Para o private demo individual, preferir o **Cloudflare identity provider** da própria organização Zero Trust. Contas novas do Zero Trust já podem vir com ele como IdP padrão.

Isso evita criar um armazenamento de senha próprio e evita uma dependência adicional só para a demo.

Mais tarde podemos adicionar Entra ID, Google Workspace ou outro IdP sem alterar o domínio do NOC Flow.

## 4. Obter Team Domain e AUD

Na configuração do Access, obter:

- **Team Domain**: `https://<team>.cloudflareaccess.com`;
- **Application Audience (AUD) Tag** da aplicação NOC Flow.

Esses valores não são senhas, mas devem ser configurados por ambiente e não hardcoded no código.

Preencher `.env.private`:

```text
NOCFLOW_ENVIRONMENT=staging
NOCFLOW_AUTH_MODE=cloudflare_access
NOCFLOW_CLOUDFLARE_ACCESS_TEAM_DOMAIN=https://<team>.cloudflareaccess.com
NOCFLOW_CLOUDFLARE_ACCESS_AUDIENCE=<AUD-da-aplicacao>
NOCFLOW_CLOUDFLARE_ACCESS_TENANT_ID=00000000-0000-4000-8000-000000000001
NOCFLOW_CLOUDFLARE_ACCESS_BOOTSTRAP_ADMIN_EMAIL=<email-autorizado>
```

## 5. Bootstrap do primeiro Admin

Para evitar cadastro aberto, o NOC Flow não cria usuários arbitrariamente.

No private demo existe um bootstrap restrito:

1. o request precisa ter JWT Cloudflare Access válido;
2. o e-mail validado precisa coincidir exatamente com `NOCFLOW_CLOUDFLARE_ACCESS_BOOTSTRAP_ADMIN_EMAIL`;
3. se o tenant configurado ainda não existir, ele é criado como `private-demo`; se já existir, precisa estar ativo;
4. o ambiente não pode ser `production`;
5. o backend cria `user + membership(Admin)` se ainda não existirem; usuário ou tenant inativos nunca são reativados pelo bootstrap.

Após o primeiro login bem-sucedido e a criação da membership, remover da configuração local:

```text
NOCFLOW_CLOUDFLARE_ACCESS_BOOTSTRAP_ADMIN_EMAIL
```

A membership persistida passa a ser a autoridade de autorização.

## 6. Subir o ambiente

```powershell
docker compose --env-file .env.private -f compose.private.yaml up -d --build
```

Validar:

```powershell
docker compose --env-file .env.private -f compose.private.yaml ps
```

Esperado:

- `postgres`: healthy;
- `backend`: healthy;
- `web`: healthy;
- `cloudflared`: running.

Nenhum desses serviços deve publicar diretamente `4200`, `8000` ou `5432` no host.

## 7. Teste de autenticação

No dispositivo inscrito no Cloudflare One Client:

```text
http://nocflow.internal
```

Fluxo esperado:

```text
sem sessão Access
    ↓
login Cloudflare Access
    ↓
policy Allow
    ↓
NOC Flow
    ↓
GET /api/v1/auth/me
    ↓
Admin / Supervisor / Operator / Viewer
```

Validar também:

- identidade não permitida pelo Access não alcança a aplicação;
- token Access ausente/inválido no origin retorna `401`;
- identidade válida sem membership retorna `403`;
- Viewer não recebe ações de escrita;
- Operator/Supervisor/Admin respeitam a matriz RBAC;
- IDs de outro tenant não vazam dados.

## Parar

```powershell
docker compose --env-file .env.private -f compose.private.yaml down
```

Para remover também os dados sintéticos persistidos:

```powershell
docker compose --env-file .env.private -f compose.private.yaml down -v
```

## Evolução com domínio próprio

O private network não será descartado quando houver domínio.

```text
seudominio.com              -> portfólio principal
nocflow.seudominio.com      -> NOC Flow Cloud v2
careerops.seudominio.com    -> CareerOps
lab.seudominio.com          -> laboratórios selecionados
dev.seudominio.com          -> ambiente protegido por Access
```

A autenticação interna do NOC Flow permanece baseada em identidade externa validada + membership interna, independentemente de o front door futuro ser Cloudflare Access ou OIDC direto.

## O que NÃO fazer

- não liberar política `Everyone`;
- não usar `Bypass` para contornar autenticação;
- não expor `backend:8000` diretamente;
- não expor PostgreSQL;
- não confiar em header de identidade sem validar assinatura JWT;
- não aceitar role enviada pelo browser ou pelo token externo;
- não colocar token/cookie/JWT no GitHub, Trello ou logs;
- não adicionar dados corporativos reais;
- não chamar este ambiente de produção.

## Gate de homologação

- Tunnel saudável;
- `nocflow.internal` roteado como private hostname;
- aplicação Access configurada para `nocflow.internal:80`;
- login pelo IdP funciona;
- JWT Access validado no backend;
- bootstrap do primeiro Admin funciona somente para o e-mail configurado;
- bootstrap removido após criar a membership;
- `/api/v1/auth/me` retorna contexto autorizado;
- usuário sem membership recebe `403`;
- RBAC validado no backend e refletido no Angular;
- criação/listagem/detalhe/update/normalização/timeline funcionam;
- filtros/paginação funcionam;
- nenhuma porta da aplicação/banco publicada;
- secrets ausentes do Git;
- somente dados sintéticos.
