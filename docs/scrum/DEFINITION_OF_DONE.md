# Definition of Done — P0 NOC Flow Cloud v2

Uma User Story somente pode ser considerada **Done** quando todos os itens aplicáveis forem satisfeitos.

## Produto

- comportamento atende aos critérios de aceite;
- estados vazio, loading, erro e permissão foram considerados;
- textos e labels são compreensíveis para a operação;
- nenhuma regra importante existe apenas na memória do desenvolvedor.

## Código

- tipagem adequada;
- lint e format passam;
- não há TODO crítico escondendo requisito de escopo;
- responsabilidades estão no módulo correto;
- não há dependência circular conhecida;
- migration acompanha qualquer alteração de schema.

## Testes

- unit tests cobrem regras de domínio relevantes;
- integration test existe quando há DB/API;
- recurso tenant-scoped novo possui teste cross-tenant;
- E2E é atualizado quando fluxo crítico muda;
- bug corrigido recebe teste de regressão quando reproduzível;
- critérios de aceite possuem evidência verificável.

## Segurança

- autorização é validada no backend;
- inputs são validados;
- nenhum secret ou dado real foi adicionado;
- logs foram revisados para evitar exposição sensível;
- mudança de permissão/auditoria foi revisada quando aplicável.

## UX e acessibilidade

- fluxo funciona por teclado quando aplicável;
- foco é previsível;
- contraste e semântica são adequados;
- ação destrutiva possui proteção proporcional ao risco;
- feedback do sistema não bloqueia trabalho rotineiro sem necessidade.

## Observabilidade

- erros possuem código e contexto útil;
- endpoint novo relevante possui logs/métricas apropriados;
- request ID é preservado em falhas quando aplicável.

## Documentação

- OpenAPI reflete mudanças da API;
- ADR foi criado/atualizado se decisão arquitetural significativa mudou;
- README, runbook ou documentação operacional foram atualizados se o modo de executar mudou;
- screenshots/diagramas foram atualizados quando necessário;
- changelog foi atualizado quando a alteração entra em release.

## CI/CD

- pipeline está verde;
- build é reproduzível;
- security checks aplicáveis foram executados;
- deploy, quando aplicável, passou smoke test.

## Revisão

- PR descreve problema, solução e testes;
- alteração não mistura refatoração extensa sem relação com a história;
- reviewer consegue entender impacto sem depender de contexto oral;
- apontamentos BLOCKER/MAJOR de Code Review foram resolvidos ou formalmente devolvidos ao time responsável.

## Regra

Trabalho parcialmente implementado, não testado ou não documentado permanece em andamento e não é contabilizado como Done.