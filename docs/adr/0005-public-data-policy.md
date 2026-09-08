# ADR-0005 — Repositório público usa somente dados sintéticos

**Status:** Accepted  
**Data:** 2026-09-08

## Contexto

Ferramentas de NOC podem conter dados operacionais, contatos, circuitos e identificadores sensíveis. O projeto é público e de portfólio.

## Decisão

Nenhum dado derivado de operação real será usado em seeds, fixtures, screenshots, documentação, issues, PRs ou exemplos.

## Convenções

- tenants: `Operação Aurora`, `Operação Horizonte` ou outros nomes inventados;
- sites: códigos `DEMO-*`;
- operadoras: marcas fictícias nos dados públicos;
- designações: `CIR-DEMO-*`;
- telefones/endereço: omitidos ou claramente reservados para exemplo;
- protocolos: `INC-DEMO-*`.

## Consequência

É proibido “anonimizar superficialmente” export real. O dado de demo deve ser criado do zero para evitar identificadores residuais/metadados.