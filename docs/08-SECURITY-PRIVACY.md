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

- OIDC/OAuth2 com validação de assinatura/JWKS, issuer, audience, expiração e algoritmos permitidos;
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

## RBAC implementado na Sprint 3

Roles internas vigentes: `Admin`, `Supervisor`, `Operator` e `Viewer`.

| Permissão | Admin | Supervisor | Operator | Viewer |
|---|---:|---:|---:|---:|
| `incident:read` | ✓ | ✓ | ✓ | ✓ |
| `incident:create` | ✓ | ✓ | ✓ | — |
| `incident:update` | ✓ | ✓ | ✓ | — |
| `incident:normalize` | ✓ | ✓ | ✓ | — |

As permissions são calculadas server-side a partir da role persistida em `tenant_memberships`. Claims externos de role/group não são autoridade de autorização.

Novas permissões para handover, administração, auditoria ou platform administration devem ser adicionadas explicitamente quando o incremento correspondente for implementado; não devem ser inferidas antecipadamente a partir da nomenclatura da role.

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

## Extensão RBAC implementada — Sprint 4

A Sprint 4 adicionou permissions explícitas sem alterar a autoridade das roles externas:

| Permissão | Admin | Supervisor | Operator | Viewer |
|---|---:|---:|---:|---:|
| `handover:read` | ✓ | ✓ | ✓ | ✓ |
| `handover:finalize` | ✓ | ✓ | ✓ | — |

Regras:

- `GET /dashboard/summary` exige `incident:read`;
- `GET /handovers/preview`, `GET /handovers/latest` e `GET /handovers/{id}` exigem `handover:read`;
- `POST /handovers` exige `handover:finalize`;
- tenant continua vindo do contexto autenticado;
- handover de outro tenant é tratado como não encontrado para evitar enumeração;
- cliente não envia tenant, autor, versão ou itens como autoridade;
- observações são texto livre validado e nunca devem ser renderizadas como HTML não escapado;
- logs não registram body completo de observações.

### Ameaças específicas da Sprint 4

- IDOR/BOLA em handover por UUID;
- elevação de Viewer para finalização;
- forging de tenant/autor/versão/itens;
- corrida entre duas finalizações;
- alteração retroativa de snapshot;
- XSS em observações;
- vazamento cross-tenant em agregados do dashboard.

As mitigações obrigatórias são authorization server-side, tenant scoping, constraints transacionais, snapshot imutável, validação Pydantic, escaping no frontend e testes negativos dedicados.
