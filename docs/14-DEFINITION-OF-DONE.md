# Definition of Done

Uma story só pode ser considerada concluída quando todos os itens aplicáveis forem satisfeitos.

## Produto

- comportamento atende critérios de aceite;
- estados vazio/loading/erro/permissão foram considerados;
- textos e labels são compreensíveis para operação;
- nenhuma regra importante existe somente na memória do desenvolvedor.

## Código

- tipagem adequada;
- lint/format passam;
- não há TODO crítico escondendo requisito do escopo;
- responsabilidades estão no módulo correto;
- não há dependência circular conhecida;
- migration acompanha mudança de schema.

## Testes

- unit tests para regra de domínio;
- integration test quando há DB/API;
- teste cross-tenant para recurso tenant-scoped novo;
- E2E atualizado quando fluxo crítico muda;
- bug corrigido recebe teste de regressão quando reproduzível.

## Segurança

- autorização validada no backend;
- inputs validados;
- nenhum secret/dado real adicionado;
- logs revisados para evitar informação sensível;
- mudança de permissão/auditoria revisada quando aplicável.

## UX/Acessibilidade

- teclado funciona no fluxo;
- foco é previsível;
- contraste/semântica adequados;
- ação destrutiva tem proteção proporcional;
- toast/modal não bloqueia trabalho rotineiro sem necessidade.

## Observabilidade

- erros têm código/contexto útil;
- endpoint novo relevante possui métricas/logs apropriados;
- request ID é preservado em falhas.

## Documentação

- OpenAPI reflete API;
- ADR criado se decisão arquitetural significativa mudou;
- README/runbook atualizado se modo de executar mudou;
- changelog atualizado em release.

## CI/CD

- pipeline verde;
- build reproduzível;
- deploy, quando aplicável, passou smoke check.

## Revisão

- PR descreve problema, solução e testes;
- não mistura refatoração extensa sem relação com a story;
- reviewer consegue entender impacto sem contexto oral obrigatório.