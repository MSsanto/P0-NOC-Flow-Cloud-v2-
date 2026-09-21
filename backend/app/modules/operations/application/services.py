from datetime import UTC, datetime, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.modules.incidents.domain.entities import IncidentSeverity
from app.modules.operations.application.ports import OperationsRepository
from app.modules.operations.domain.entities import (
    DashboardSummary,
    Handover,
    HandoverPage,
    HandoverPreview,
    ShiftWindow,
)


class ShiftConfigurationError(ValueError):
    pass


class HandoverNotFoundError(LookupError):
    pass


class HandoverVersionConflictError(RuntimeError):
    pass


def calculate_shift_window(
    *,
    timezone_name: str,
    shift_start_local,
    shift_duration_minutes: int,
    now: datetime,
) -> ShiftWindow:
    try:
        zone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise ShiftConfigurationError("Tenant timezone is invalid.") from exc
    if (
        shift_duration_minutes < 60
        or shift_duration_minutes > 1440
        or 1440 % shift_duration_minutes != 0
    ):
        raise ShiftConfigurationError("Tenant shift duration is invalid.")

    local_now = now.astimezone(zone)
    anchor = datetime.combine(local_now.date(), shift_start_local, tzinfo=zone)
    if local_now < anchor:
        anchor -= timedelta(days=1)

    elapsed_minutes = int((local_now - anchor).total_seconds() // 60)
    slot = elapsed_minutes // shift_duration_minutes
    start_local = anchor + timedelta(minutes=slot * shift_duration_minutes)
    end_local = start_local + timedelta(minutes=shift_duration_minutes)
    return ShiftWindow(
        window_start=start_local.astimezone(UTC),
        window_end=end_local.astimezone(UTC),
    )


class OperationsService:
    def __init__(self, repository: OperationsRepository) -> None:
        self.repository = repository

    def _window(self, tenant_id: UUID, now: datetime) -> ShiftWindow:
        timezone_name, shift_start_local, duration = self.repository.get_shift_configuration(
            tenant_id
        )
        return calculate_shift_window(
            timezone_name=timezone_name,
            shift_start_local=shift_start_local,
            shift_duration_minutes=duration,
            now=now,
        )

    def dashboard(self, tenant_id: UUID, now: datetime | None = None) -> DashboardSummary:
        current = now or datetime.now(UTC)
        window = self._window(tenant_id, current)
        items = self.repository.list_dashboard_items(tenant_id)
        return DashboardSummary(
            active_count=len(items),
            critical_active_count=sum(
                item.severity is IncidentSeverity.CRITICAL for item in items
            ),
            resolved_in_shift_count=self.repository.count_resolved_in_window(
                tenant_id, window
            ),
            shift=window,
            items=items,
        )

    def preview(self, tenant_id: UUID, now: datetime | None = None) -> HandoverPreview:
        current = now or datetime.now(UTC)
        window = self._window(tenant_id, current)
        return HandoverPreview(
            window_start=window.window_start,
            window_end=window.window_end,
            generated_at=current,
            items=self.repository.list_handover_items(tenant_id, window),
        )

    def finalize(
        self,
        *,
        tenant_id: UUID,
        actor_subject: str,
        observations: str | None,
        now: datetime | None = None,
    ) -> Handover:
        current = now or datetime.now(UTC)
        window = self._window(tenant_id, current)
        items = self.repository.list_handover_items(tenant_id, window)
        return self.repository.create_handover(
            tenant_id,
            actor_subject,
            window,
            observations,
            items,
        )

    def history(self, tenant_id: UUID, page: int, page_size: int) -> HandoverPage:
        return self.repository.list_handovers(tenant_id, page, page_size)

    def latest(self, tenant_id: UUID) -> Handover:
        handover = self.repository.get_latest_handover(tenant_id)
        if handover is None:
            raise HandoverNotFoundError
        return handover

    def get(self, tenant_id: UUID, handover_id: UUID) -> Handover:
        handover = self.repository.get_handover(tenant_id, handover_id)
        if handover is None:
            raise HandoverNotFoundError
        return handover
