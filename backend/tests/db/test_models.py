from app.db.base import Base
from app.db.models import IncidentModel, TenantModel


def test_sprint1_metadata_registers_tenant_and_incident() -> None:
    assert TenantModel.__table__ is Base.metadata.tables["tenants"]
    assert IncidentModel.__table__ is Base.metadata.tables["incidents"]


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
