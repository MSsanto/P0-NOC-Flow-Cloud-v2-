# apps/web

Reservado para a aplicação Angular do NOC Flow Cloud v2.

**P0:** nenhum código de aplicação deve existir aqui ainda.

## Responsabilidades futuras

- shell da aplicação;
- autenticação OIDC no navegador;
- seleção/contexto de operação;
- dashboard;
- incidentes/timeline;
- handover;
- base operacional/administração;
- acessibilidade e temas.

## Limites

- autorização final pertence à API;
- não armazenar tokens em locais inseguros;
- não duplicar regra de domínio crítica apenas no front;
- APIs consumidas via `/api/v1`.