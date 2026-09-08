# ADR-0002 — Multi-tenancy por `tenant_id` em schema compartilhado

**Status:** Accepted  
**Data:** 2026-09-08

## Contexto

O produto deve servir múltiplas operações sem forks e sem misturar dados.

## Decisão

Usar inicialmente um PostgreSQL compartilhado e schema compartilhado, com `tenant_id` obrigatório em entidades de negócio e autorização baseada em memberships.

## Regras

- tenant nunca é inferido de dado não autenticado;
- todo repository tenant-scoped recebe contexto explícito;
- foreign keys e queries validam coerência do tenant;
- IDs de outro tenant são tratados como não encontrados para usuário comum;
- testes de vazamento são gate obrigatório;
- RLS poderá ser adicionada como defesa adicional após protótipo, sem substituir checks de aplicação.

## Consequências

Positivas: custo baixo, migrations simples, analytics possível, adequado ao porte inicial.

Riscos: uma query incorreta pode vazar dados. Por isso tenant scoping não pode depender de disciplina informal e será encapsulado/testado.

## Alternativas

- database por tenant: isolamento forte, custo/operação maiores;
- schema por tenant: migrations e observabilidade mais complexas para o estágio atual.