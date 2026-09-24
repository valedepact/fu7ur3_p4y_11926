from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Dict, List

from .interfaces import LoadRepository


class GetPeakHours:
    """Use case: how many loads were dropped off in each hour of the day."""

    def __init__(self, load_repo: LoadRepository):
        self._load_repo = load_repo

    def execute(self, start: date, end: date) -> Dict[int, int]:
        loads = self._load_repo.list_between(start, end)
        counts: Dict[int, int] = defaultdict(int)
        for l in loads:
            counts[l.dropped_off_at.hour] += 1
        return dict(sorted(counts.items()))


@dataclass
class ItemClassPopularity:
    item_class_id: int
    load_count: int
    total_revenue: float


class GetItemClassPopularity:
    """Use case: which item classes bring in the most loads and revenue."""

    def __init__(self, load_repo: LoadRepository):
        self._load_repo = load_repo

    def execute(self, start: date, end: date) -> List[ItemClassPopularity]:
        loads = self._load_repo.list_between(start, end)
        totals: Dict[int, ItemClassPopularity] = {}
        for l in loads:
            for item in l.items:
                entry = totals.setdefault(
                    item.item_class_id,
                    ItemClassPopularity(item_class_id=item.item_class_id, load_count=0, total_revenue=0),
                )
                entry.load_count += 1
                entry.total_revenue += item.total
        return sorted(totals.values(), key=lambda e: e.total_revenue, reverse=True)