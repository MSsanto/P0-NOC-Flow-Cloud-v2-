# Estratégia de testes

## Pirâmide

```text
          E2E (poucos, críticos)
       Integration / Contract
    Unit / Domain (maior volume)
```

## Backend

### Unitários

- transições de estado;
- regras de correlação;
- renderização de templates;
- cálculo de turno;
- permissions/policies;
- validações de domínio.

Ferramenta planejada: `pytest`.

### Integração

- repositories com PostgreSQL real em container;
- migrations;
- isolamento por tenant;
- transações;
- endpoints FastAPI + auth fake controlada;
- OpenAPI/contrato.

Evitar validar PostgreSQL apenas com SQLite quando o comportamento depender de recursos diferentes.

## Front-end

### Unit/component

- componentes de formulário;
- guards/contexto de tenant;
- presentation state;
- validações e estados de erro.

### E2E

Ferramenta planejada: Playwright.

Fluxos mínimos:

1. login simulado/demo;
2. selecionar operação;
3. criar incidente;
4. registrar atualização;
5. normalizar;
6. gerar handover;
7. usuário sem permissão não acessa administração;
8. tenant A nunca exibe recurso do tenant B.

## Testes de segurança

- IDOR/BOLA cross-tenant;
- role escalation;
- inputs maliciosos em resumo/template;
- CORS;
- headers;
- secrets scan;
- dependency vulnerabilities.

## Testes de acessibilidade

- checks automatizados em páginas críticas;
- navegação por teclado manual;
- foco em modais/toasts;
- contraste e labels.

## Testes de performance

Começam após o core estabilizar. Cenários:

- listar incidentes ativos;
- abrir timeline longa;
- busca por período;
- geração de handover.

Metas são registradas antes da execução para evitar ajustar critério ao resultado.

## Fixtures

Somente dados sintéticos. Fixtures nunca serão copiadas de produção.

## Gate de CI planejado

PR só fica elegível para merge quando:

- lint passa;
- type checks passam;
- unit tests passam;
- integration tests essenciais passam;
- build passa;
- secret/dependency checks não têm bloqueio crítico;
- cobertura não cai abaixo do threshold acordado após baseline.

Cobertura é indicador, não substituto de qualidade.

## Matriz de testes da Sprint 4

### Cálculo de turno

- tenant em timezone sem DST;
- instante exatamente no início do turno;
- instante imediatamente antes/depois do limite;
- turno atravessando meia-noite;
- timezone com transição DST usando IANA;
- `shift_duration_minutes` inválido rejeitado por constraint/configuração;
- limites persistidos no handover correspondem ao value object calculado.

### Dashboard — US-011

**Unit/integration**

- agregação ignora `RESOLVED`/`CLOSED` em `active_count`;
- `critical_active_count` considera somente ativos CRITICAL;
- normalização dentro da janela entra em `resolved_in_shift_count`;
- normalização fora da janela não entra;
- ordenação por severidade e `started_at`;
- tenant A nunca agrega dados do tenant B;
- sem `incident:read` retorna 403.

**Frontend**

- loading;
- empty state;
- dados carregados;
- erro com retry;
- 401;
- 403;
- navegação por teclado nos cards.

### Handover preview — US-012

- inclui incidentes ativos;
- inclui incidentes com `INCIDENT_NORMALIZED` dentro do turno;
- remove duplicidade quando incidente se enquadra em mais de uma seleção;
- ignora normalização fora da janela;
- tenant isolation;
- Viewer com `handover:read` pode consultar preview;
- preview não persiste registros.

### Finalização — US-012

- Admin/Supervisor/Operator finalizam;
- Viewer recebe 403;
- request tentando enviar `tenant_id`, `version`, ator ou `items` recebe 422;
- handover e itens persistem atomicamente;
- falha durante itens faz rollback do pai;
- primeira finalização cria versão 1;
- nova finalização da mesma janela cria versão seguinte;
- duas transações concorrentes não persistem a mesma versão;
- conflito de versão retorna 409 `HANDOVER_VERSION_CONFLICT`;
- snapshot persiste valores do incidente no instante da finalização;
- mudança posterior no incidente não altera item já gravado;
- observação inválida é rejeitada;
- conteúdo de observação não é logado como body sensível.

### Consulta — US-013

- latest retorna a finalização mais recente do tenant;
- latest sem registro retorna 404 `HANDOVER_NOT_FOUND`;
- histórico paginado ordena por finalização desc;
- consulta por ID retorna versão histórica;
- ID de outro tenant não é exposto;
- Viewer pode consultar;
- não existem rotas HTTP de update/delete do handover.

### Migration

Executar em PostgreSQL real:

1. upgrade até head;
2. validar tabelas/constraints/índices;
3. criar handover e itens válidos;
4. comprovar unique constraint de versão;
5. comprovar unique de item por handover/incidente.

### E2E crítico da Sprint 4

1. autenticar em tenant sintético;
2. visualizar dashboard;
3. abrir preview de handover;
4. finalizar passagem;
5. consultar snapshot final;
6. alterar/normalizar incidente depois;
7. confirmar que snapshot anterior permanece inalterado;
8. Viewer consulta, mas não finaliza;
9. tenant B não acessa handover do tenant A.

## Evidência mínima para Done da Sprint 4

- pytest unit/integration;
- migration PostgreSQL no CI;
- frontend unit tests;
- build;
- security/dependency audits;
- smoke full-stack do fluxo Sprint 4;
- evidência manual de teclado/401/403/409 e snapshot imutável.
