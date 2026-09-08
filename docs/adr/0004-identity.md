# ADR-0004 — Identidade baseada em OIDC/OAuth2

**Status:** Accepted  
**Data:** 2026-09-08

## Contexto

A aplicação precisa de autenticação realista para cloud sem construir armazenamento próprio de senhas como foco do projeto.

## Decisão

Adotar abstração de identidade baseada em OIDC/OAuth2. Microsoft Entra ID é o alvo principal de implantação Azure, mas o domínio deve depender apenas de claims normalizados/identidade interna.

## Desenvolvimento

Pode existir provider de desenvolvimento/demo explicitamente isolado, sem backdoor habilitado em produção.

## Regras

- senha não é armazenada pelo NOC Flow Cloud v2;
- subject externo é mapeado para user interno;
- autorização é feita com memberships internos;
- claims externos não concedem acesso a tenant sem regra explícita;
- tokens não entram em logs.

## Consequências

Reduz superfície de autenticação própria e aproxima o projeto de ambientes corporativos, ao custo de configuração adicional em dev/cloud.