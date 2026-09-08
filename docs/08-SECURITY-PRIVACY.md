# Segurança e privacidade

## Objetivo

Aplicar segurança desde o desenho, especialmente porque o domínio pode conter informações operacionais sensíveis em implantações privadas.

## Modelo de ameaça resumido

Ativos:

- dados de operações e unidades;
- incidentes e timelines;
- contatos e identificadores de circuitos;
- memberships e papéis;
- tokens de identidade;
- segredos de integrações futuras;
- exports e logs.

Ameaças prioritárias:

1. vazamento cross-tenant;
2. escalada de privilégio;
3. IDOR/BOLA em recursos por ID;
4. credenciais/segredos no Git;
5. XSS por conteúdo livre/templates;
6. SQL injection;
7. excesso de dados em logs;
8. exportação indevida;
9. abuso de endpoint de integração;
10. alterações sem trilha de auditoria.

## Controles P1/P2

- OIDC/OAuth2;
- backend como autoridade de autorização;
- validação de membership em toda operação tenant-scoped;
- ORM/queries parametrizadas;
- validação Pydantic;
- política de CORS restritiva;
- CSP no front-end quando hospedagem permitir;
- escaping/sanitização para qualquer template renderizado em HTML;
- rate limiting nos endpoints expostos a integração;
- logs estruturados sem token/body sensível por padrão;
- auditoria de permissões, exports e transições críticas;
- secrets somente em secret store/env local ignorado;
- dependency scanning e secret scanning no CI quando disponível.

## RBAC inicial

| Ação | Analyst | Supervisor | Tenant Admin | Platform Admin |
|---|---:|---:|---:|---:|
| Ver incidentes | ✓ | ✓ | ✓ | conforme suporte autorizado |
| Criar/atualizar incidente | ✓ | ✓ | ✓ | — |
| Reabrir fechado | limitado | ✓ | ✓ | — |
| Finalizar handover | ✓ | ✓ | ✓ | — |
| Editar base operacional | — | limitado | ✓ | — |
| Gerir memberships | — | — | ✓ | ✓ |
| Criar tenant | — | — | — | ✓ |
| Ver auditoria | — | ✓ | ✓ | suporte autorizado |

A matriz será transformada em permissions explícitas; roles não devem virar `if role == ...` espalhados pelo código.

## Dados públicos de portfólio

Obrigatório:

- nomes de unidades inventados;
- IDs `DEMO-*` ou equivalentes;
- operadoras fictícias nos seeds públicos;
- telefones e endereços inexistentes ou reservados para exemplo;
- nenhum CNPJ real;
- nenhuma captura de tela com dado de cliente;
- nenhum export real em issues/PRs.

## Segredos

Nunca versionar:

- `.env`;
- connection strings;
- client secrets;
- tokens GitHub/Azure;
- certificados privados;
- webhooks secretos;
- dumps de banco.

Produção Azure: preferir Managed Identity + Key Vault quando aplicável.

## LGPD

O portfólio não pretende processar dados pessoais reais. Em implantação real, antes de produção deverão ser definidos finalidade, base legal, minimização, retenção, direitos do titular, operadores/controladores e procedimento de incidente de segurança conforme o contexto jurídico da organização.

Este documento é requisito de engenharia, não parecer jurídico.