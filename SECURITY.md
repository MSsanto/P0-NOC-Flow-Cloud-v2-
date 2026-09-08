# Política de segurança

## Escopo

Este repositório é um projeto público de portfólio e ainda não possui release de aplicação em produção.

## Reporte

Não publique detalhes exploráveis, credenciais ou dados sensíveis em issue pública. Para uma vulnerabilidade real em uma futura versão implantada, use um canal privado disponibilizado no perfil/repositório quando esse canal for configurado.

## Dados proibidos no repositório

- tokens e chaves;
- `.env` reais;
- credenciais Azure/GitHub/DB;
- dados de clientes/operações;
- CNPJ/endereço/telefone real de operação;
- circuitos/designações reais;
- dumps/backups;
- screenshots operacionais não sanitizados.

## Prioridades de segurança

1. isolamento de tenant;
2. autorização no backend;
3. proteção de segredos;
4. prevenção de XSS/injection;
5. auditoria;
6. logging seguro;
7. dependências e supply chain.

Veja `docs/08-SECURITY-PRIVACY.md`.