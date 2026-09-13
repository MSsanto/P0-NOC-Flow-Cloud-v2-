# Cloudflare Private Demo — NOC Flow Cloud v2

## Objetivo

Disponibilizar o NOC Flow Cloud v2 remotamente para demonstração privada sem expor portas do host para Internet e sem tratar o ambiente como produção.

O desenho usa:

- Docker Compose;
- `cloudflared` como conexão de saída;
- Cloudflare Tunnel;
- Cloudflare Access como camada de autenticação antes da aplicação;
- dados exclusivamente sintéticos;
- identidade demo do NOC Flow, permitida somente em `development`/`test`.

## Limite de segurança

Este ambiente é **private demo**, não produção.

O provider de identidade atual do NOC Flow é deliberadamente bloqueado fora de `development`/`test`. Portanto, não alterar `NOCFLOW_ENVIRONMENT` para `production` apenas para hospedar esta demo. Produção real continua dependendo de OIDC/RBAC e demais gates do roadmap.

## Arquitetura

```text
Browser autorizado
       |
       v
Cloudflare Access
       |
       v
Cloudflare Tunnel
       |
       v
cloudflared (Docker)
       |
       v
web :80 (Nginx)
   | /api/v1
   v
backend :8000
       |
       v
PostgreSQL :5432
```

Nenhum dos serviços `postgres`, `backend` ou `web` publica `ports:` em `compose.private.yaml`. O único caminho esperado de entrada é o túnel.

## Preparação local

Copie `.env.example` para um arquivo local ignorado pelo Git, por exemplo `.env.private`.

Gere uma senha forte para `POSTGRES_PASSWORD` e nunca reutilize a senha de desenvolvimento padrão.

Não cole nem versione o token do Cloudflare Tunnel. O token concede capacidade para executar uma réplica do túnel e deve ser tratado como secret.

## Ordem segura no Cloudflare

A ordem é importante: configure o Access **antes** de publicar a rota do túnel.

### 1. Criar a aplicação no Cloudflare Access

No Cloudflare Zero Trust:

1. `Access controls` → `Applications`;
2. criar aplicação `Self-hosted and private`;
3. adicionar o hostname que será usado pelo NOC Flow;
4. criar uma política `Allow` restrita somente aos usuários autorizados;
5. usar um IdP configurado ou e-mail OTP;
6. manter o comportamento deny-by-default;
7. configurar sessão curta para ambiente de demonstração.

Se for usado um hostname público protegido por Access, o DNS pode ser resolvível publicamente, mas a aplicação não é entregue sem autenticação/autorização no Access.

Para um modo estritamente sem DNS público, usar a variante de private network do Cloudflare One/One Client. Essa opção exige o cliente Cloudflare One no dispositivo e configuração de rota privada.

### 2. Criar o Tunnel

No Cloudflare Dashboard:

1. `Networking` → `Tunnels`;
2. criar `noc-flow-private-demo`;
3. selecionar Docker como método de execução;
4. copiar apenas o token para o arquivo local `.env.private`;
5. nunca adicionar o token ao GitHub, Trello, documentação ou logs.

### 3. Configurar a rota

Para o modo de hostname protegido por Access, configure o serviço de origem do Tunnel como:

```text
http://web:80
```

`cloudflared` e `web` compartilham a rede interna criada pelo Docker Compose, portanto `web` é resolvido pelo DNS interno do Docker.

## Subir o private demo

```bash
docker compose --env-file .env.private -f compose.private.yaml up -d --build
```

Validar:

```bash
docker compose --env-file .env.private -f compose.private.yaml ps
```

Esperado:

- `postgres`: healthy;
- `backend`: healthy;
- `web`: healthy;
- `cloudflared`: running.

O host não deve escutar as portas `4200`, `8000` ou `5432` por causa deste Compose.

## Parar

```bash
docker compose --env-file .env.private -f compose.private.yaml down
```

Para remover também os dados sintéticos persistidos:

```bash
docker compose --env-file .env.private -f compose.private.yaml down -v
```

## Política de acesso recomendada

Para a primeira demo:

- `Include`: somente os e-mails explicitamente autorizados;
- nenhum `Bypass`;
- nenhum `Everyone`;
- OTP ou IdP;
- sessão curta;
- revisar Access logs após testes.

## O que NÃO fazer

- não expor `backend:8000` diretamente na Internet;
- não expor PostgreSQL;
- não usar Quick Tunnel (`trycloudflare.com`) para a demo persistente;
- não colocar token do Tunnel no repositório;
- não adicionar dados corporativos reais;
- não chamar este ambiente de produção;
- não desabilitar Access para simplificar a demonstração.

## Gate antes de considerar o ambiente utilizável

- Access criado e deny-by-default;
- usuário não autorizado recebe bloqueio antes do NOC Flow;
- usuário autorizado consegue autenticar;
- Tunnel saudável;
- aplicação abre via HTTPS no endereço Cloudflare;
- criação/listagem/detalhe/update/normalização/timeline funcionam;
- filtros/paginação funcionam;
- nenhuma porta da aplicação/banco está publicada pelo Compose privado;
- token e senha ausentes do Git;
- somente dados sintéticos.
