from datetime import time
from typing import Protocol
from uuid import UUID

from app.modules.operations.domain.entities import (
    DashboardItem,
    Handover,
    HandoverItem,
    HandoverPage,
    ShiftWindow,
)


class OperationsRepository(Protocol):
    def get_shift_configuration(self, tenant_id: UUID) -> tuple[str, time, int]: ...
    def list_dashboard_items(self, tenant_id: UUID) -> list[DashboardItem]: ...
    def count_resolved_in_window(self, tenant_id: UUID, window: ShiftWindow) -> int: ...
    def list_handover_items(self, tenant_id: UUID, window: ShiftWindow) -> list[HandoverItem]: ...
    def create_handover(
        self,
        tenant_id: UUID,
        actor_subject: str,
        window: ShiftWindow,
        observations: str | None,
        items: list[HandoverItem],
    ) -> Handover: ...
    def list_handovers(self, tenant_id: UUID, page: int, page_size: int) -> HandoverPage: ...
    def get_latest_handover(self, tenant_id: UUID) -> Handover | None: ...
    def get_handover(self, tenant_id: UUID, handover_id: UUID) -> Handover | None: ...
