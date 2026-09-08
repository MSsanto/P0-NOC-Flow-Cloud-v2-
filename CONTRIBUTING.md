# Contribuindo

## Estado atual

O projeto está em P0 documental. Mudanças de implementação não devem ser abertas antes da aprovação do P0.

## Fluxo futuro

1. abrir/associar issue;
2. criar branch curta;
3. implementar uma mudança focada;
4. adicionar/ajustar testes;
5. atualizar documentação;
6. abrir PR usando o template;
7. aguardar CI/revisão;
8. preferir squash merge para histórico de features, salvo decisão posterior.

## Convenção de branches sugerida

- `feat/...`
- `fix/...`
- `docs/...`
- `refactor/...`
- `test/...`
- `chore/...`

## Commits

Preferência planejada por Conventional Commits:

- `feat:`
- `fix:`
- `docs:`
- `test:`
- `refactor:`
- `chore:`

## Regras públicas

- nunca anexar export real;
- nunca colar token/log sensível em issue;
- screenshots devem ser revisados;
- novas dependências precisam de justificativa;
- decisão arquitetural significativa exige ADR;
- PR deve permanecer pequeno o suficiente para revisão efetiva.