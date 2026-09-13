from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from app.modules.incidents.presentation.schemas import (
    IncidentCreateRequest,
    IncidentNormalizeRequest,
    IncidentUpdateRequest,
)


def test_incident_create_schema_accepts_canonical_payload() -> None:
    payload = IncidentCreateRequest(
        title="WAN outage",
        affected_resource="WAN",
        severity="HIGH",
        impact_type="OUTAGE",
        symptoms="Connectivity is unavailable",
        started_at=datetime.now(UTC) - timedelta(minutes=1),
    )

    assert payload.title == "WAN outage"
    assert payload.severity.value == "HIGH"


def test_incident_create_schema_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        IncidentCreateRequest(
            title="WAN outage",
            affected_resource="WAN",
            severity="HIGH",
            impact_type="OUTAGE",
            symptoms="Connectivity is unavailable",
            started_at=datetime.now(UTC),
            tenant_id="00000000-0000-4000-8000-000000000001",
        )


def test_update_schema_strips_whitespace_and_rejects_short_message() -> None:
    payload = IncidentUpdateRequest(message="  Operadora acionada.  ")
    assert payload.message == "Operadora acionada."

    with pytest.raises(ValidationError):
        IncidentUpdateRequest(message="  x ")


def test_normalize_schema_rejects_authority_fields() -> None:
    with pytest.raises(ValidationError):
        IncidentNormalizeRequest(
            note="Serviço restabelecido.",
            actor_subject="forged-actor",
        )
