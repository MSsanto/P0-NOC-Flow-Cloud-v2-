# ADR-0004 — Identidade baseada em OIDC/OAuth2

**Status:** Accepted  
**Data:** 2026-09-08  
**Atualizado:** 2026-09-15 — Sprint 3

## Contexto

A aplicação precisa de autenticação realista para cloud sem construir armazenamento próprio de senhas como foco do projeto.

## Decisão

Adotar abstração de identidade baseada em OIDC/OAuth2. Microsoft Entra ID é o alvo principal de implantação Azure, mas o domínio depende apenas de identidade externa validada e de autorização interna.

O backend valida access tokens por assinatura, issuer, audience, expiração e algoritmos permitidos configurados pelo servidor. A resolução de autorização é deliberadamente separada da autenticação.

## Contrato de identidade

O token externo fornece:

- `sub`: identificador imutável do usuário no IdP;
- claim configurável `tenant_id`: tenant solicitado para a requisição.

O token **não é autoridade de role ou permissão**. Mesmo quando o IdP fornecer roles/groups, o NOC Flow não concede acesso com base neles nesta etapa.

Após validar o token, o backend exige:

1. `users.external_subject == sub` e usuário ativo;
2. tenant solicitado existente e ativo;
3. `tenant_memberships` ativa para aquele usuário + tenant;
4. role interna válida (`Admin`, `Supervisor`, `Operator` ou `Viewer`).

Somente então é construído o `RequestContext` tenant-scoped.

## Desenvolvimento

Pode existir provider de desenvolvimento/demo explicitamente isolado. Ele é permitido apenas em `development`/`test`, cria um usuário/membership sintético e nunca funciona como fallback em staging/produção.

## Regras

- senha não é armazenada pelo NOC Flow Cloud v2;
- subject externo é mapeado para usuário interno;
- autorização é feita com memberships internos;
- claims externos não concedem acesso a tenant sem membership explícita;
- roles e permissões não são confiadas a payload do cliente;
- algoritmos JWT permitidos vêm da configuração do servidor, não do header do token;
- tokens e headers de autorização não entram em logs;
- autenticação ausente/inválida retorna 401;
- identidade autenticada sem membership/permissão retorna 403;
- recursos de outro tenant permanecem invisíveis pelas queries tenant-scoped.

## Consequências

Reduz superfície de autenticação própria, impede elevação de privilégio por claim externo e aproxima o projeto de ambientes corporativos. O custo é manter provisioning/memberships internos e configurar o IdP em cada ambiente.
