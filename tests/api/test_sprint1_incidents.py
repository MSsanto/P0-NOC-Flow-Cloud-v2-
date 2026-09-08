import os
from datetime import datetime, timedelta, timezone

import pytest

pytestmark = pytest.mark.integration


DATETIME_FIELDS = {"started_at", "detected_at", "created_at"}


def _items(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return payload["items"]
    pytest.fail("GET /incidents deve retornar lista JSON ou objeto com campo items[]")


def _assert_list_item_contract(item: dict) -> None:
    assert "id" in item, "incidente listado sem id"
    assert "status" in item, "incidente listado sem status"
    assert "severity" in item, "incidente listado sem severity"
    assert DATETIME_FIELDS.intersection(item), (
        "incidente listado sem data/hora; esperado ao menos um de "
        f"{sorted(DATETIME_FIELDS)}"
    )


def test_qa_001_list_incidents_contract(api_client):
    response = api_client.get("/incidents")

    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", "")

    for item in _items(response.json()):
        assert isinstance(item, dict)
        _assert_list_item_contract(item)


def test_qa_005_unknown_incident_returns_404(api_client):
    # ULID sintético, bem formado e reservado apenas para teste negativo.
    missing_id = "01ZZZZZZZZZZZZZZZZZZZZZZZZ"
    response = api_client.get(f"/incidents/{missing_id}")

    assert response.status_code == 404
    assert "application/json" in response.headers.get("content-type", "")


def test_qa_005_known_incident_detail(api_client):
    incident_id = os.getenv("NOC_KNOWN_INCIDENT_ID")
    if not incident_id:
        pytest.skip("NOC_KNOWN_INCIDENT_ID não configurado para validar detalhe real")

    response = api_client.get(f"/incidents/{incident_id}")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert payload.get("id") == incident_id
    assert "status" in payload
    assert "severity" in payload


@pytest.mark.xfail(
    strict=True,
    reason="P0-QA-BLOCKER-001 / GitHub #6: contrato canônico de POST /incidents ainda divergente",
)
def test_qa_003_create_valid_incident_trello_candidate_contract(api_client):
    now = datetime.now(timezone.utc)
    payload = {
        "summary": "Indisponibilidade WAN sintética para teste QA",
        "affected_resource": "Circuito WAN QA-001",
        "severity": "HIGH",
        "impact_type": "OUTAGE",
        "description": "Perda total de conectividade observada em cenário sintético.",
        "started_at": (now - timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
    }

    response = api_client.post("/incidents", json=payload)

    assert response.status_code == 201
    created = response.json()
    assert created["status"] == "OPEN"
    assert created.get("id")
    assert created.get("created_at")
    assert created.get("updated_at")
    assert "tenant" in created or "tenant_id" in created
    assert "author" in created or "author_id" in created


@pytest.mark.xfail(
    strict=True,
    reason="P0-QA-BLOCKER-001 / GitHub #6: contrato canônico de POST /incidents ainda divergente",
)
def test_qa_004_create_rejects_missing_required_fields(api_client):
    response = api_client.post("/incidents", json={"summary": "Sem campos obrigatórios"})

    assert response.status_code in {400, 422}


@pytest.mark.xfail(
    strict=True,
    reason="P0-QA-BLOCKER-001 / GitHub #6: contrato canônico de POST /incidents ainda divergente",
)
def test_qa_004_create_rejects_future_start_without_partial_record(api_client):
    future = datetime.now(timezone.utc) + timedelta(hours=1)
    payload = {
        "summary": "Incidente futuro inválido para teste QA",
        "affected_resource": "Circuito WAN QA-002",
        "severity": "MEDIUM",
        "impact_type": "DEGRADATION",
        "description": "Payload sintético propositalmente inválido para validar regra temporal.",
        "started_at": future.isoformat().replace("+00:00", "Z"),
    }

    response = api_client.post("/incidents", json=payload)

    assert response.status_code in {400, 422}
