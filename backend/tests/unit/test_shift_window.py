from datetime import UTC, datetime, time

from app.modules.operations.application.services import calculate_shift_window


def test_shift_window_uses_configured_anchor_and_duration() -> None:
    window = calculate_shift_window(
        timezone_name="UTC",
        shift_start_local=time(6, 0),
        shift_duration_minutes=720,
        now=datetime(2026, 9, 21, 17, 30, tzinfo=UTC),
    )
    assert window.window_start == datetime(2026, 9, 21, 6, 0, tzinfo=UTC)
    assert window.window_end == datetime(2026, 9, 21, 18, 0, tzinfo=UTC)


def test_shift_window_rolls_to_previous_day_before_anchor() -> None:
    window = calculate_shift_window(
        timezone_name="UTC",
        shift_start_local=time(6, 0),
        shift_duration_minutes=720,
        now=datetime(2026, 9, 21, 5, 59, tzinfo=UTC),
    )
    assert window.window_start == datetime(2026, 9, 20, 18, 0, tzinfo=UTC)
    assert window.window_end == datetime(2026, 9, 21, 6, 0, tzinfo=UTC)
