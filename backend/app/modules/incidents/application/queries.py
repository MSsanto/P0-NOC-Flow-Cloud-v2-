from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.modules.incidents.domain.entities import Incident, IncidentSeverity, IncidentStatus


class IncidentSortField(StrEnum):
    STARTED_AT = "started_at"
    UPDATED_AT = "updated_at"


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


@dataclass(frozen=True, slots=True)
class IncidentListQuery:
    status: IncidentStatus | None = None
    severity: IncidentSeverity | None = None
    started_from: datetime | None = None
    started_to: datetime | None = None
    page: int = 1
    page_size: int = 25
    sort: IncidentSortField = IncidentSortField.STARTED_AT
    order: SortOrder = SortOrder.DESC

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


@dataclass(frozen=True, slots=True)
class IncidentPage:
    items: list[Incident]
    page: int
    page_size: int
    total: int

    def __iter__(self) -> Iterator[Incident]:
        return iter(self.items)
