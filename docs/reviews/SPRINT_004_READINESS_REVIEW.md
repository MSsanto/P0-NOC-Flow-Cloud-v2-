# Sprint 004 — Readiness Review

**Data:** 2026-09-21  
**Escopo:** revisão documental pré-implementação  
**Issue:** #47  
**Branch:** `docs/sprint4-readiness`

## Objetivo

Verificar se US-011, US-012 e US-013 atendem à Definition of Ready sem depender de decisões essenciais durante a implementação.

Esta revisão foi feita sobre os artefatos versionados, sem assumir contexto oral e sem alterar código de aplicação.

## Artefatos revisados

- `docs/02-REQUIREMENTS.md`
- `docs/04-DOMAIN-MODEL.md`
- `docs/05-DATA-MODEL.md`
- `docs/06-API-CONTRACT.md`
- `docs/07-UX-FLOWS.md`
- `docs/08-SECURITY-PRIVACY.md`
- `docs/09-TEST-STRATEGY.md`
- `docs/15-RISKS.md`
- `docs/17-TRACEABILITY.md`
- `docs/adr/0008-handover-snapshot-versioning.md`
- `docs/scrum/SPRINT_004.md`

## Checklist DoR

### Produto

- [x] problema e benefício claros;
- [x] atores identificados;
- [x] critérios de aceite objetivos por story;
- [x] prioridade definida;
- [x] escopo da Sprint delimitado.

### Dependências

- [x] boundary Incident/Handover decidido em ADR-0008;
- [x] modelo físico planejado;
- [x] contrato HTTP planejado;
- [x] UX definida para dashboard, preview, finalização e consulta;
- [x] configuração de turno definida por tenant;
- [x] nenhuma dependência de protocol/next-step futuro é exigida pelo snapshot.

### Testabilidade

- [x] cenários unit/integration/frontend/E2E derivados;
- [x] cross-tenant definido;
- [x] Viewer 403 definido;
- [x] concorrência/version conflict definido;
- [x] imutabilidade histórica verificável;
- [x] dados de teste exclusivamente sintéticos.

### Execução

- [x] responsáveis/especialistas mapeados;
- [x] baseline de entrada verde;
- [x] riscos específicos registrados;
- [x] implementação permanece bloqueada até merge deste readiness.

### Documentação

- [x] requisitos atualizados;
- [x] ADR criado;
- [x] domínio e dados atualizados;
- [x] contrato API documentado;
- [x] segurança e permissions documentadas;
- [x] estratégia de testes e rastreabilidade atualizadas.

## Achados da revisão e resolução

### R1 — Janela de turno era ambígua

**Risco:** apenas `timezone` existia no tenant, sem anchor/duração.

**Resolução:** ADR-0008 e modelo planejado definem `shift_start_local` + `shift_duration_minutes`, com value object de turno e testes de boundary/DST.

### R2 — Snapshot antecipava campos ainda não implementados

**Risco:** acoplar Sprint 4 a protocolos/próximo passo.

**Resolução:** schema do snapshot usa apenas Incident/IncidentEvent já executáveis. Campos futuros ficam fora.

### R3 — Preview e observações estavam semanticamente misturados

**Risco:** um `GET` parecer responsável por estado do operador.

**Resolução:** preview é read-only e calculado; observações só existem no comando de finalização.

### R4 — Histórico não tinha descoberta de versões

**Risco:** versões antigas existirem, mas a UI não conseguir encontrá-las.

**Resolução:** adicionado contrato `GET /handovers` paginado.

### R5 — Backfill de configuração de turno estava contraditório

**Risco:** migration impossível de aplicar com `NOT NULL` em tenants existentes.

**Resolução:** novas tabelas não exigem backfill; campos de turno exigem backfill explícito antes de `NOT NULL`.

### R6 — Handover vazio não estava definido

**Risco:** turno sem incidentes gerar comportamento ambíguo.

**Resolução:** finalização com zero itens é válida e registra explicitamente um turno sem incidentes selecionados.

## Resultado

**READY**, condicionado ao merge do pacote documental com gates verdes.

A implementação deve seguir os contratos deste readiness. Qualquer alteração material em snapshot, janela de turno, permissions, endpoints ou schema exige atualizar documentação e, se arquitetural, superseder/alterar ADR antes do código correspondente.
