# tests

Diretório para suítes transversais, contratos, smoke e E2E. Testes específicos de módulo podem residir próximos ao código conforme convenção definida no scaffold.

## Sprint 1 — EN-009

A primeira suíte executável de QA está na branch `qa/sprint-1-en-009`.

### Python / API + smoke

Dependências:

```bash
python -m pip install -r tests/requirements-qa.txt
```

Execução planejada:

```bash
NOC_API_BASE_URL=http://127.0.0.1:8000/api/v1 \
NOC_WEB_BASE_URL=http://127.0.0.1:4200 \
pytest tests/api tests/smoke -q
```

Variável opcional:

- `NOC_KNOWN_INCIDENT_ID`: ID de fixture sintético existente para teste positivo de detalhe.

Quando as variáveis de ambiente não estão configuradas, os testes black-box são `skip`; isso **não** constitui evidência de aceite. Teste crítico pulado, `xfail` ou não executado mantém o item fora de Done.

Os testes de criação estão temporariamente `xfail(strict=True)` por causa do `P0-QA-BLOCKER-001` (GitHub #6), que registra divergência no contrato de `POST /incidents`.

## Suítes planejadas

- unit/domain com `pytest` junto ao backend quando o scaffold existir;
- integration/API com PostgreSQL real;
- E2E Playwright;
- security/cross-tenant;
- contract/OpenAPI;
- smoke pós-deploy;
- performance posteriormente.

Todos os dados devem ser sintéticos.

## Documentação

A rastreabilidade e os casos da Sprint 1 estão em `docs/qa/SPRINT_1_QA_PLAN.md`.
