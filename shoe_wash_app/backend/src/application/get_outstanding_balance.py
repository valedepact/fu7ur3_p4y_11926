from datetime import date

from .interfaces import LoadRepository


class GetOutstandingBalance:
    """Use case: total amount owed across every customer, right now."""

    def __init__(self, load_repo: LoadRepository):
        self._load_repo = load_repo

    def execute(self) -> float:
        all_loads = self._load_repo.list_between(date(2000, 1, 1), date.today())
        return sum(l.total - l.amount_paid for l in all_loads if l.amount_paid < l.total)