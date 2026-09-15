# Cloudflare Private Demo — NOC Flow Cloud v2

## Objetivo

Disponibilizar o NOC Flow Cloud v2 remotamente para demonstração **sem publicar a aplicação na Internet** e sem tratar o ambiente como produção.

O modo atual usa:

- Docker Compose;
- `cloudflared` como conexão de saída;
- Cloudflare Tunnel;
- Cloudflare One Client (WARP) no dispositivo autorizado;
- hostname privado `nocflow.internal`;
- Cloudflare Access/Gateway para restringir acesso;
- dados exclusivamente sintéticos;
- identidade demo do NOC Flow, permitida somente em `development`/`test`.

Cloudflare Tunnel é outbound-only. Nenhuma porta de entrada do host precisa ser aberta.

## Limite de segurança

Este ambiente é **private demo**, não produção.

O provider de identidade atual do NOC Flow é deliberadamente bloqueado fora de `development`/`test`. Não alterar `NOCFLOW_ENVIRONMENT` para `production` apenas para hospedar esta demo. Produção real continua dependendo de OIDC/RBAC e dos gates previstos no roadmap.

## Arquitetura atual — sem domínio público

```text
Notebook autorizado
       |
Cloudflare One Client / WARP
       |
Cloudflare Access + Gateway
       |
Cloudflare Tunnel
       |
cloudflared (Docker)
       |
       v
nocflow.internal -> web :80 (Nginx)
                         | /api/v1
                         v
                    backend :8000
                         |
                         v
                    PostgreSQL :5432
```

Nenhum dos serviços `postgres`, `backend` ou `web` publica `ports:` em `compose.private.yaml`.

O serviço `web` possui o alias Docker `nocflow.internal`. Como `cloudflared` está na mesma rede Docker, o hostname privado pode ser resolvido pelo DNS interno do Docker para alcançar o Nginx.

## Preparação local

Copie `.env.example` para um arquivo local ignorado pelo Git:

```bash
cp .env.example .env.private
```

No PowerShell:

```powershell
Copy-Item .env.example .env.private
```

Gere uma senha forte para `POSTGRES_PASSWORD`.

Não cole nem versione o token do Cloudflare Tunnel. O token concede capacidade para executar uma réplica do túnel e deve ser tratado como secret.

## Configuração Cloudflare atual — private network

### 1. Ativar Zero Trust

No dashboard Cloudflare, inicialize o Cloudflare Zero Trust para a conta e defina o nome da organização.

### 2. Criar o Tunnel

1. `Networking` → `Tunnels`;
2. criar `noc-flow-private-demo`;
3. selecionar Docker como método de execução;
4. copiar somente o token para `.env.private` como `CLOUDFLARE_TUNNEL_TOKEN`;
5. nunca adicionar o token ao GitHub, Trello, documentação ou logs.

Não adicionar uma rota `Published application` enquanto o objetivo for manter o NOC Flow fora da Internet pública.

### 3. Adicionar rota de hostname privado

No Tunnel:

1. abrir `Routes`;
2. adicionar `Private hostname`;
3. hostname: `nocflow.internal`;
4. salvar a rota apontando para o Tunnel `noc-flow-private-demo`.

Para hostname privado, o dispositivo cliente precisa enviar DNS e tráfego pela rede Cloudflare One. O Cloudflare Gateway atribui um endereço intermediário e encaminha a conexão para o Tunnel.

### 4. Restringir acesso

Criar uma aplicação Access para o hostname privado `nocflow.internal` e permitir somente usuários explicitamente autorizados.

Configuração inicial recomendada:

- Allow: somente o e-mail do proprietário do projeto;
- nenhum `Everyone`;
- nenhum `Bypass`;
- política de bloqueio para os demais;
- sessão curta;
- revisar Access/Gateway logs após os testes.

### 5. Instalar Cloudflare One Client

Instalar o Cloudflare One Client no dispositivo que acessará o NOC Flow e fazer o enrollment na organização Zero Trust.

Usar o modo de tráfego/DNS compatível com private hostname routing e garantir que o tráfego destinado aos endereços iniciais resolvidos pelo Gateway não esteja excluído pelas regras de Split Tunnel.

A referência oficial deve ser seguida para qualquer ajuste de Split Tunnel, porque essa configuração depende do perfil do dispositivo.

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

No dispositivo inscrito no Cloudflare One, testar:

```text
http://nocflow.internal
```

O hostname não depende de DNS público nem de domínio registrado.

## Parar

```bash
docker compose --env-file .env.private -f compose.private.yaml down
```

Para remover também os dados sintéticos persistidos:

```bash
docker compose --env-file .env.private -f compose.private.yaml down -v
```

## Evolução quando houver domínio próprio

O private network atual não será descartado. Quando um domínio for registrado e adicionado à Cloudflare, poderemos publicar somente os projetos aprovados e manter ambientes internos privados.

Estrutura sugerida:

```text
seudominio.com              -> portfólio principal
nocflow.seudominio.com      -> NOC Flow Cloud v2
careerops.seudominio.com    -> CareerOps, quando aprovado para publicação
lab.seudominio.com          -> projetos/laboratórios selecionados
dev.seudominio.com          -> opcional, protegido por Access
```

Para o NOC Flow, a futura mudança será majoritariamente de entrada:

```text
hoje:    nocflow.internal -> WARP -> Tunnel -> web
futuro:  nocflow.seudominio.com -> Access -> Tunnel -> web
```

Angular, FastAPI e PostgreSQL permanecem atrás do mesmo Nginx e não precisam ser reescritos apenas por causa do domínio.

Cloudflare exige um domínio conectado à conta para usar `Published application` com hostname público. Por isso esse passo fica para a fase em que o domínio for adquirido.

## O que NÃO fazer

- não adicionar `Published application` enquanto quisermos zero exposição pública;
- não expor `backend:8000` diretamente;
- não expor PostgreSQL;
- não usar Quick Tunnel (`trycloudflare.com`) como ambiente persistente;
- não colocar token do Tunnel no repositório;
- não adicionar dados corporativos reais;
- não chamar este ambiente de produção;
- não liberar política `Everyone` para simplificar a demo.

## Gate antes de considerar o ambiente utilizável

- Tunnel saudável;
- `nocflow.internal` configurado como private hostname;
- Cloudflare One Client inscrito no dispositivo;
- usuário autorizado consegue acessar;
- usuário não autorizado é bloqueado;
- criação/listagem/detalhe/update/normalização/timeline funcionam;
- filtros/paginação funcionam;
- nenhuma porta da aplicação/banco está publicada pelo Compose privado;
- token e senha ausentes do Git;
- somente dados sintéticos.
