# Security Documentation

Este diretório organiza a documentação técnica de segurança do P0 — NOC Flow Cloud v2.

## Referências atuais

- [Segurança e privacidade](../08-SECURITY-PRIVACY.md)
- [Política pública de segurança](../../SECURITY.md)

## Escopo documental

- autenticação e autorização;
- multi-tenancy e isolamento;
- threat model;
- validação de inputs;
- secrets e configuração;
- logging seguro;
- segurança de API;
- dependências;
- CI/CD e supply chain;
- segurança Azure;
- auditoria e rastreabilidade.

## Referências de engenharia

As análises devem considerar OWASP Top 10, OWASP API Security, least privilege, secure by default e defense in depth.

## Regra de manutenção

Achados de segurança devem registrar severidade, impacto e mitigação prática. Vulnerabilidades Critical ou High não devem ser tratadas apenas como pendência documental para permitir release.