# Sprint 1 — Plano de QA

Escopo: `EN-009 — QA Strategy & Sprint 1 Tests [P0]`.

Data da primeira execução: 2026-09-08.

## Estado do ambiente

Na baseline analisada, `apps/api` e `apps/web` contêm somente documentação de reserva e `tests/` ainda não possuía suíte executável. Portanto, os testes podem ser preparados agora, mas não existe aplicação para produzir evidência verde.

Também há divergência no contrato de criação de incidente entre US-002, RF-005 e `docs/06-API-CONTRACT.md`. O impedimento está registrado no GitHub como `P0-QA-BLOCKER-001` (#6).

## Rastreabilidade EN-009

| Task | Critério | Cobertura planejada/automatizada | Estado atual |
|---|---|---|---|
| TASK-QA-001 | API de listagem | `tests/api/test_sprint1_incidents.py::test_qa_001_list_incidents_contract` | Preparado; execução bloqueada por API inexistente |
| TASK-QA-002 | Frontend de listagem | cenários funcionais abaixo + Playwright após scaffold/rotas estáveis | Bloqueado por EN-004/UX |
| TASK-QA-003 | criação válida | `test_qa_003_create_valid_incident_trello_candidate_contract` | Automatizado como `xfail(strict=True)` até resolução do #6 |
| TASK-QA-004 | criação inválida/negativa | testes negativos em `test_sprint1_incidents.py` | Automatizado como `xfail(strict=True)` até resolução do #6 |
| TASK-QA-005 | detalhe/404 | `test_qa_005_unknown_incident_returns_404` e `test_qa_005_known_incident_detail` | Preparado; execução bloqueada por API inexistente |
| TASK-QA-006 | smoke FE+BE+DB | `tests/smoke/test_sprint1_smoke.py` | Preparado; execução bloqueada por ambiente inexistente |

## US-001 — Listar incidentes

### API

- `QA-S1-US001-001` — `GET /api/v1/incidents` retorna `200` e JSON.
- `QA-S1-US001-002` — resposta vazia é válida e não produz erro.
- `QA-S1-US001-003` — cada item existente possui ID, status, severidade e data/hora.
- `QA-S1-US001-004` — falha inesperada deve manter resposta de erro consistente e request ID quando o tratamento estiver implementado.
- `QA-S1-US001-005` — tenant não autorizado nunca aparece na coleção quando multi-tenancy entrar no vertical slice.

### Frontend

- `QA-S1-US001-FE-001` — exibe loading enquanto request está pendente.
- `QA-S1-US001-FE-002` — exibe estado vazio quando API retorna coleção vazia.
- `QA-S1-US001-FE-003` — exibe erro recuperável quando API falha.
- `QA-S1-US001-FE-004` — renderiza ID, status, severidade e data/hora para cada item.
- `QA-S1-US001-FE-005` — refresh não deixa tela em estado inconsistente.
- `QA-S1-US001-FE-006` — navegação por teclado e semântica acessível devem ser verificadas no componente final.

## US-002 — Criar incidente

Até o contrato ser unificado, os nomes exatos de campos permanecem bloqueados. Os seguintes comportamentos são obrigatórios segundo o backlog da Sprint 1:

- `QA-S1-US002-001` — criação válida retorna `201` e incidente persistido.
- `QA-S1-US002-002` — status inicial é `OPEN`.
- `QA-S1-US002-003` — ID, `created_at` e `updated_at` são gerados pelo sistema.
- `QA-S1-US002-004` — tenant e autor não podem ser definidos livremente pelo cliente.
- `QA-S1-US002-005` — título/resumo aceita 3 e 120 caracteres; rejeita 2 e 121.
- `QA-S1-US002-006` — recurso/serviço aceita 2 e 120 caracteres; rejeita 1 e 121.
- `QA-S1-US002-007` — severidade aceita somente `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`.
- `QA-S1-US002-008` — impacto aceita somente `OUTAGE`, `DEGRADATION`.
- `QA-S1-US002-009` — descrição aceita 10 e 2000 caracteres; rejeita 9 e 2001.
- `QA-S1-US002-010` — início igual ao momento atual é aceito dentro da tolerância definida; início futuro é rejeitado.
- `QA-S1-US002-011` — ausência de qualquer obrigatório retorna erro claro e não cria registro parcial.
- `QA-S1-US002-012` — JSON malformado e tipos incompatíveis são rejeitados.
- `QA-S1-US002-013` — tentativa de injetar `tenant`, `tenant_id`, `author` ou `author_id` não altera o contexto autorizado.
- `QA-S1-US002-014` — falha de persistência não deixa registro parcial.

## US-003 — Visualizar detalhe

- `QA-S1-US003-001` — ID existente retorna `200` e dados completos.
- `QA-S1-US003-002` — ID inexistente bem formado retorna `404`.
- `QA-S1-US003-003` — recurso de outro tenant deve parecer inexistente quando isolamento estiver habilitado.
- `QA-S1-US003-004` — refresh da rota preserva o contexto do incidente.
- `QA-S1-US003-005` — frontend trata loading, erro e não encontrado sem quebrar navegação.

## Smoke Sprint 1

- API liveness responde `200`.
- API readiness responde `200` somente quando dependências essenciais, incluindo DB, estão prontas.
- Frontend responde `200` e entrega conteúdo.
- Após existir vertical slice, smoke deverá executar `criar -> listar -> detalhar` com dados sintéticos e limpeza/isolamento apropriados.

## Comandos previstos

```bash
python -m pip install -r tests/requirements-qa.txt
NOC_API_BASE_URL=http://127.0.0.1:8000/api/v1 \
NOC_WEB_BASE_URL=http://127.0.0.1:4200 \
pytest tests/api tests/smoke -q
```

`NOC_KNOWN_INCIDENT_ID` é opcional e habilita a validação de detalhe de um fixture conhecido.

## Gate de QA

A Sprint 1 não pode receber aceite de QA enquanto qualquer uma das condições abaixo existir:

- aplicação/ambiente não executável;
- teste crítico apenas `skip`, `xfail` ou não executado;
- contrato #6 sem decisão;
- P0/BLOCKER aberto sem mitigação aprovada;
- smoke FE+BE+DB sem evidência verde;
- critérios de aceite P0 sem rastreabilidade verificável.

## Veredito atual

**NÃO ELEGÍVEL PARA DONE / QA BLOQUEADO.**

A suíte inicial foi preparada, mas a implementação necessária para executá-la ainda não existe e o contrato de criação permanece inconsistente.
