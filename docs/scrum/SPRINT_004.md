# Sprint 004 — Dashboard & Passagem de Turno

**Status:** Concluída tecnicamente — aguardando homologação manual da candidata `v0.4.0-beta`  
**Duração planejada:** 2 semanas  
**Release alvo:** `v0.4.0-beta`  
**Sprint Goal:** permitir continuidade operacional entre turnos com visão rápida dos incidentes e pendências.

## Gate de entrada

A Sprint só pode mudar para **Ready / Em execução** quando:

- critérios de aceite abaixo estiverem aprovados;
- ADR-0008 estiver aceito;
- modelo de dados físico estiver documentado;
- contrato HTTP estiver documentado;
- permissions de handover estiverem documentadas;
- cenários QA/cross-tenant/concurrency estiverem definidos;
- UX do preview/finalização/consulta estiver definida;
- baseline do `main` estiver verde.

Baseline de entrada validado em 21/09/2026, commit `e9bf9d4f66337117860160e81e01f27754e84c63`:

- CI: success;
- Sprint 2 Functional Smoke: success;
- Private Demo Compose: success.

## User Stories

### US-011 — Dashboard operacional [P0]

Como operador NOC, quero visualizar rapidamente incidentes ativos, críticos e pendências para priorizar minha atuação.

**Responsável primário:** 04 Frontend  
**Dependências:** 05 Backend, 07 QA, 09 Security.

#### Critérios de aceite

1. usuário autenticado com permissão de leitura acessa o dashboard apenas do tenant ativo;
2. dashboard apresenta contagens de incidentes ativos e críticos usando dados reais da API;
3. apresenta fila de incidentes ordenada por prioridade operacional definida para o incremento;
4. loading, vazio, erro recuperável, 401 e 403 possuem estado explícito;
5. nenhuma métrica de produtividade não medida é exibida;
6. cards funcionam como navegação/filtro e não substituem a lista detalhada;
7. dados de outro tenant nunca entram nos agregados;
8. frontend não calcula autorização nem redefine regras críticas do backend.

### US-012 — Criar passagem de turno [P0]

Como operador que encerra o turno, quero registrar uma passagem estruturada para transferir contexto e próximos passos ao operador seguinte.

**Responsável primário:** 05 Backend & API  
**Dependências:** 01 PO, 02 Architecture, 03 UX/UI, 06 Database, 07 QA, 09 Security.

#### Critérios de aceite

1. operador autorizado consegue solicitar preview tenant-scoped do turno atual;
2. preview inclui incidentes ativos e incidentes relevantes resolvidos no turno conforme regra documentada;
3. operador pode adicionar observações antes da finalização;
4. finalização cria snapshot persistido com autoria, UTC, janela de turno e versão definidos server-side;
5. handover finalizado não possui endpoint de update/delete;
6. nova correção gera nova versão, sem alterar versões anteriores;
7. duas finalizações concorrentes não podem produzir a mesma versão;
8. Viewer recebe 403 ao tentar finalizar;
9. tentativa cross-tenant não revela existência do recurso;
10. falha transacional durante persistência não pode deixar pai/itens parcialmente gravados; preview vazio pode ser finalizado legitimamente com zero itens.

### US-013 — Consultar passagem de turno [P0]

Como operador que inicia o turno, quero consultar a passagem anterior para assumir a operação sem perder contexto.

**Responsável primário:** 04 Frontend  
**Dependências:** 05 Backend, 07 QA, 09 Security.

#### Critérios de aceite

1. usuário com `handover:read` consulta o handover mais recente do tenant ativo;
2. pode consultar uma versão específica por ID dentro do tenant autorizado;
3. conteúdo exibido vem do snapshot persistido e não muda quando o incidente original evolui;
4. autoria, horário, janela de turno e versão ficam visíveis;
5. versões anteriores permanecem consultáveis;
6. estado sem handover possui empty state compreensível;
7. 401, 403, 404 e erro recuperável possuem tratamento explícito;
8. recurso pertencente a outro tenant não é exposto.

## Conteúdo mínimo do handover

O snapshot da Sprint 4 deve possuir informação suficiente para continuidade sem copiar toda a timeline:

- identificador do incidente;
- título/recurso afetado;
- severidade;
- status no snapshot;
- instante de início;
- última atualização disponível, quando existir;
- observações gerais do handover;
- autoria;
- timestamps;
- janela do turno;
- versão.

Campos ainda não implementados em Incident não devem ser inventados apenas para preencher o handover; o contrato deve refletir o estado real do domínio.

## Decisão arquitetural

ADR-0008 define:

- preview calculado e não persistido;
- handover final como snapshot;
- finalizado é imutável;
- correção cria nova versão;
- janela de turno calculada, sem entidade Shift persistida na Sprint 4;
- concorrência deve resultar em conflito explícito, nunca overwrite.

## Permissions alvo

- `handover:read`: Admin, Supervisor, Operator, Viewer;
- `handover:finalize`: Admin, Supervisor, Operator.

A autorização continua server-side e derivada das memberships internas.

## Distribuição por especialistas

- **01 PO:** regra e conteúdo obrigatório do handover.
- **02 Architecture:** boundaries entre Incident e Handover; ADR-0008.
- **03 UX/UI:** dashboard de baixa carga cognitiva e fluxo preview → finalizar → consultar.
- **04 Frontend:** dashboard e consulta/finalização conforme contrato aprovado.
- **05 Backend:** agregados do dashboard, preview e finalização/consulta de handover.
- **06 Database:** schema, constraints, índices e migration.
- **07 QA:** vazio, múltiplos incidentes, concorrência, imutabilidade e cross-tenant.
- **08 DevOps:** manter gates e observabilidade básica do fluxo.
- **09 Security:** permissions, IDOR/BOLA e tenant isolation.
- **10 Docs:** domínio, dados, API, UX, segurança, testes e rastreabilidade.
- **11 Review:** review independente.
- **12 Release:** homologação `v0.4.0-beta`.

## Tasks de readiness

- [x] TASK-PO-S4-01 problema e conteúdo mínimo definidos;
- [x] TASK-ARC-S4-01 decisão de snapshot/versionamento registrada no ADR-0008;
- [x] TASK-UX-S4-01 contrato UX do dashboard;
- [x] TASK-UX-S4-02 contrato UX do handover;
- [x] TASK-DB-S4-01 schema físico e migration planejados;
- [x] TASK-BE-S4-00 contrato HTTP antes do código;
- [x] TASK-QA-S4-00 matriz de cenários e evidências;
- [x] TASK-SEC-S4-00 permissions alvo definidas;
- [x] TASK-DOC-S4-00 rastreabilidade completa;
- [x] TASK-CR-S4-00 revisão documental adversarial registrada em `docs/reviews/SPRINT_004_READINESS_REVIEW.md`.

## Tasks de implementação

- [x] TASK-BE-S4-01 criar/finalizar handover;
- [x] TASK-BE-S4-02 consultar handovers;
- [x] TASK-FE-S4-01 dashboard;
- [x] TASK-FE-S4-02 editor/preview;
- [x] TASK-FE-S4-03 consulta e histórico;
- [x] TASK-QA-S4-01 fluxo de passagem, regressão e smoke ponta a ponta;
- [x] TASK-SEC-S4-01 autorização, least privilege e tenant isolation;
- [x] TASK-DOC-S4-01 documentação pós-implementação e evidências;
- [x] TASK-CR-S4-01 review independente/adversarial do incremento;
- [ ] TASK-REL-S4-01 homologação manual da candidata `v0.4.0-beta`.

A única atividade restante é a homologação humana descrita em
`docs/releases/V0.4.0-BETA-HOMOLOGATION.md`.

## Critérios de sucesso da Sprint

- operador identifica rapidamente a situação atual do tenant;
- passagem pode ser finalizada e consultada;
- snapshot não muda retroativamente;
- histórico preserva autoria, timestamps e versões;
- isolamento por tenant permanece válido;
- concorrência não sobrescreve versões;
- testes críticos e security checks verdes;
- release homologada.
