# Sprint 4 — resumo e evidências

**Incremento:** Dashboard & Passagem de Turno  
**Estado:** concluído tecnicamente em 21/09/2026; aguardando homologação manual  
**Release candidata:** `v0.4.0-beta`

## Resultado

A Sprint 4 adiciona continuidade operacional entre turnos sem tornar o handover uma consulta dinâmica. O backend calcula a janela de turno pelo tenant, gera preview server-side e finaliza snapshots versionados e imutáveis. O frontend passa a oferecer Dashboard e Passagem de Turno como superfícies principais da operação.

## Entregas

- dashboard tenant-scoped com ativos, críticos e normalizados no turno;
- fila ativa ordenada por severidade e antiguidade;
- configuração de turno por tenant;
- preview de handover sem draft persistido;
- finalização transacional de handover + itens;
- snapshots imutáveis mesmo após evolução do incidente;
- versionamento monotônico por tenant/janela;
- latest, histórico paginado e consulta por ID;
- permissions `handover:read` e `handover:finalize`;
- Viewer com leitura e sem finalização;
- UI Angular de Dashboard e Passagem de Turno;
- Sprint 4 Functional Smoke.

## Persistência

Migration:

`backend/alembic/versions/20260921_0004_shift_handovers.py`

Adiciona:

- `tenants.shift_start_local`;
- `tenants.shift_duration_minutes`;
- `handovers`;
- `handover_items`;
- constraints/índices de versão e consulta.

## API

Implementado:

```text
GET  /api/v1/dashboard/summary
GET  /api/v1/handovers/preview
POST /api/v1/handovers
GET  /api/v1/handovers
GET  /api/v1/handovers/latest
GET  /api/v1/handovers/{handover_id}
```

## Evidências automatizadas

Na rodada validada do PR de implementação:

- Backend Ruff — success;
- Alembic/PostgreSQL — success;
- pytest — success;
- pip-audit — success;
- API readiness — success;
- Angular type-check — success;
- Angular unit tests — success;
- production build — success;
- npm audit — success;
- Frontend Foundation — success;
- Cloudflare Private UI — success;
- Private Demo Compose — success;
- Sprint 2 Functional Smoke — success;
- Sprint 4 Functional Smoke — success.

## Segurança validada

- tenant, ator, versão e itens continuam server authority;
- payload com `tenant_id` forjado é rejeitado;
- autorização continua server-side;
- Viewer não recebe `handover:finalize`;
- snapshots finalizados não possuem update/delete HTTP;
- consultas de handover são tenant-scoped;
- observações são validadas como texto e não são autoridade para itens.

## O que ainda exige humano

Somente a homologação manual da experiência: leitura visual do Dashboard/Passagem, clareza da confirmação de snapshot imutável, comportamento de foco/teclado e acesso real à demo privada protegida.

O roteiro está em `docs/releases/V0.4.0-BETA-HOMOLOGATION.md`.
