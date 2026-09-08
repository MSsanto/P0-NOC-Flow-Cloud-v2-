# Definition of Ready — P0 NOC Flow Cloud v2

Uma User Story está **Ready** para Sprint Planning quando todos os critérios aplicáveis abaixo estiverem atendidos.

## Produto

- problema e benefício estão claros;
- persona ou ator está identificado;
- história está descrita em linguagem compreensível;
- critérios de aceite são objetivos e verificáveis;
- prioridade foi definida pelo Product Owner;
- escopo está pequeno o suficiente para caber em uma Sprint ou foi quebrado em fatias menores.

## Dependências

- dependências técnicas e funcionais estão identificadas;
- decisões arquiteturais necessárias já foram tomadas ou existe ADR aprovado;
- alterações de modelo de dados foram alinhadas com Database & Data Model;
- contratos de API necessários foram definidos ou há responsável explícito para defini-los antes da implementação dependente;
- design/UX necessário está disponível para fluxos visuais relevantes.

## Testabilidade

- QA consegue derivar cenários de teste a partir dos critérios de aceite;
- casos negativos e limites relevantes foram considerados;
- dados de teste necessários podem ser criados sem utilizar dados reais ou sensíveis;
- requisitos de segurança e autorização estão explicitados quando aplicável.

## Execução

- responsável principal e especialistas envolvidos são conhecidos;
- não existe impedimento conhecido que torne a história inviável na Sprint;
- ambiente, ferramenta ou acesso essencial está disponível ou possui plano explícito de resolução;
- riscos relevantes foram registrados.

## Documentação

- impacto esperado em documentação foi identificado;
- mudança arquitetural prevê ADR quando necessário;
- mudança de API prevê atualização de OpenAPI/documentação;
- mudança operacional prevê atualização de runbook/deploy quando aplicável.

## Regra

Uma história que não atende à Definition of Ready pode permanecer no Product Backlog para refinamento, mas não deve ser tratada como compromisso de Sprint até que os impedimentos sejam resolvidos.