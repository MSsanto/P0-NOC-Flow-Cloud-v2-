# Sprint 001 — Fundação executável

**Status:** Planejamento  
**Período:** a definir no Sprint Planning  
**Sprint Goal proposto:** concluir a transição da fundação documental para uma base de projeto executável, testável e reproduzível, sem comprometer segurança ou arquitetura.

> Este arquivo registra preparação de Sprint. O escopo somente se torna compromisso após validação pelo Product Owner e Sprint Planning coordenado pelo Scrum Master.

## Backlog candidato

### P0-016 — Revisar ADRs e aprovar início do P1
- validar decisões arquiteturais essenciais;
- eliminar decisões críticas pendentes antes de implementação;
- registrar aprovação ou ressalvas.

### P1-001 — Scaffold do repositório
- consolidar estrutura de frontend, backend, tests e infrastructure conforme decisão arquitetural final;
- documentar scripts e pré-requisitos;
- versionar lockfiles aplicáveis.

### P1-002 — Ambiente local
- disponibilizar backend e PostgreSQL localmente;
- criar health checks;
- documentar configuração por ambiente;
- garantir execução sem dependência obrigatória da Azure.

### P1-010 — CI inicial
- lint;
- testes;
- build;
- checks de segurança básicos em Pull Request.

## Dependências

- revisão final dos ADRs;
- definição das versões exatas de Python, Node e Angular;
- definição de gerenciador de dependências Python;
- definição de ORM/migrations;
- alinhamento da estrutura definitiva do repositório entre Architecture, Frontend, Backend e DevOps.

## Critérios de sucesso da Sprint

- repositório pode ser clonado e executado seguindo documentação;
- health check do backend funciona;
- banco local é inicializável de forma reproduzível;
- pipeline inicial executa automaticamente em PR;
- nenhum secret ou dado real é versionado;
- documentação de execução reflete o estado real do código;
- todos os itens considerados Done atendem à [Definition of Done](DEFINITION_OF_DONE.md).

## Riscos / impedimentos iniciais

| Item | Impacto | Tratamento |
|---|---|---|
| Divergência entre estrutura atual (`apps/`, `infra/`) e estrutura-alvo | Médio | decisão explícita do Software Architect antes de mover código |
| ADR essencial pendente | Alto | bloquear implementação dependente até decisão |
| Configuração local dependente de cloud | Alto | manter alternativa local obrigatória |

## Evidências da Sprint

A preencher durante a Sprint:

- Pull Requests:
- builds:
- testes:
- security checks:
- demo:
- bugs:
- documentação atualizada:

## Sprint Review

A preencher ao final:

- itens concluídos:
- itens não concluídos:
- demonstração realizada:
- feedback dos stakeholders:
- alterações propostas ao Product Backlog:

## Retrospective

Registrar conclusões consolidadas em [RETROSPECTIVES.md](RETROSPECTIVES.md).