from datetime import date, timedelta
from typing import List

from domain import Load, LoadStatus
from .interfaces import LoadRepository, BusinessSettingsRepository


class GetAbandonedLoads:
    """Use case: loads left uncollected long enough to flag as abandoned."""

    def __init__(self, load_repo: LoadRepository, settings_repo: BusinessSettingsRepository):
        self._load_repo = load_repo
        self._settings_repo = settings_repo

    def execute(self) -> List[Load]:
        settings = self._settings_repo.get()
        cutoff = date.today() - timedelta(days=settings.abandonment_days)
        candidates = self._load_repo.list_between(date(2000, 1, 1), date.today())
        return [
            l for l in candidates
            if l.status not in (LoadStatus.PICKED_UP, LoadStatus.ABANDONED)
            and l.expected_pickup_date is not None
            and l.expected_pickup_date < cutoff
        ]