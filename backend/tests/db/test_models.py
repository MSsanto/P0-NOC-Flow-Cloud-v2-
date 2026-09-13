from app.db.base import Base
from app.db.models import IncidentEventModel, IncidentModel, TenantModel


def test_sprint2_metadata_registers_tenant_incident_and_timeline() -> None:
    assert TenantModel.__table__ is Base.metadata.tables["tenants"]
    assert IncidentModel.__table__ is Base.metadata.tables["incidents"]
    assert IncidentEventModel.__table__ is Base.metadata.tables["incident_events"]


def test_incident_schema_contains_tenant_scoping_and_indexes() -> None:
    incident_table = IncidentModel.__table__

    assert incident_table.c.tenant_id.nullable is False
    assert incident_table.c.status.server_default is not None

    foreign_keys = list(incident_table.c.tenant_id.foreign_keys)
    assert len(foreign_keys) == 1
    assert foreign_keys[0].target_fullname == "tenants.id"
    assert foreign_keys[0].ondelete == "RESTRICT"

    index_names = {index.name for index in incident_table.indexes}
    assert "idx_incidents_tenant_started_at" in index_names
    assert "idx_incidents_tenant_status_started_at" in index_names


def test_incident_event_schema_is_tenant_scoped_and_indexed() -> None:
    event_table = IncidentEventModel.__table__

    assert event_table.c.tenant_id.nullable is False
    assert event_table.c.incident_id.nullable is False
    assert event_table.c.actor_subject.nullable is False
    assert event_table.c.occurred_at.nullable is False

    constraint_names = {constraint.name for constraint in event_table.constraints}
    assert "fk_incident_events_tenant_incident" in constraint_names

    index_names = {index.name for index in event_table.indexes}
    assert "idx_incident_events_tenant_incident_occurred_at" in index_names


def test_incident_contract_columns_are_present() -> None:
    column_names = set(IncidentModel.__table__.columns.keys())

    assert {
        "id",
        "tenant_id",
        "title",
        "affected_resource",
        "severity",
        "impact_type",
        "symptoms",
        "status",
        "started_at",
        "created_by_subject",
        "created_at",
        "updated_at",
        "version",
    } <= column_names
