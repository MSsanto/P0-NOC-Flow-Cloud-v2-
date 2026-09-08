# ADR-0001 — Angular + FastAPI + PostgreSQL em modular monolith

**Status:** Accepted  
**Data:** 2026-09-08

## Contexto

A v2 precisa demonstrar front-end moderno, API Python, persistência relacional, testes e cloud, sem transformar um projeto de portfólio em uma plataforma distribuída difícil de operar.

## Decisão

Adotar:

- Angular + TypeScript no front-end;
- FastAPI + Python na API;
- PostgreSQL como banco;
- monólito modular no backend;
- deploy independente de SPA e API;
- Docker para empacotamento da API;
- Azure como destino cloud planejado.

## Consequências positivas

- stack relevante para portfólio full stack/cloud;
- contratos OpenAPI naturais com FastAPI;
- PostgreSQL cobre consistência relacional e JSON quando necessário;
- uma unidade de deploy do backend simplifica transações e operação;
- limites modulares preparam extração futura.

## Trade-offs

- duas stacks/linguagens aumentam contexto de desenvolvimento;
- Angular possui estrutura maior que uma SPA mínima;
- modularidade precisa de disciplina mesmo sem barreira de serviço.

## Alternativas rejeitadas

- continuar HTML/JS/localStorage: não resolve colaboração cloud;
- microserviços: complexidade prematura;
- Next.js full stack: válido, mas não atende o objetivo deliberado de exercitar Angular + FastAPI neste projeto.