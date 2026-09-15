from dataclasses import dataclass
from datetime import date

from .interfaces import LoadRepository, ItemClassRepository, BusinessSettingsRepository


@dataclass
class DailyCapacity:
    used_minutes: int
    total_minutes: int

    @property
    def remaining_minutes(self) -> int:
        return self.total_minutes - self.used_minutes


class GetDailyCapacity:
    """Use case: how much of today's single-machine capacity is already booked."""

    def __init__(self, load_repo: LoadRepository, item_class_repo: ItemClassRepository,
                 settings_repo: BusinessSettingsRepository):
        self._load_repo = load_repo
        self._item_class_repo = item_class_repo
        self._settings_repo = settings_repo

    def execute(self, on_date: date) -> DailyCapacity:
        settings = self._settings_repo.get()
        loads = self._load_repo.list_between(on_date, on_date)
        used = sum(
            (self._item_class_repo.get(l.item_class_id).wash_minutes or 0) * l.quantity
            for l in loads
        )
        return DailyCapacity(used_minutes=used, total_minutes=settings.daily_operating_minutes)