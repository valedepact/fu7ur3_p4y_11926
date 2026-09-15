from datetime import date

from .interfaces import LoadRepository


class GetCustomerBalance:
    """Use case: how much one specific customer currently owes."""

    def __init__(self, load_repo: LoadRepository):
        self._load_repo = load_repo

    def execute(self, customer_id: int) -> float:
        all_loads = self._load_repo.list_between(date(2000, 1, 1), date.today())
        return sum(
            l.total - l.amount_paid for l in all_loads
            if l.customer_id == customer_id and l.amount_paid < l.total
        )