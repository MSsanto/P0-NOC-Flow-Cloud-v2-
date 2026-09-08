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