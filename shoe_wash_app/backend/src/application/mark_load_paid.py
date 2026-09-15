from domain import Load, PaymentStatus
from .interfaces import LoadRepository


class MarkLoadPaid:
    """Use case: record that a load has been paid in full."""

    def __init__(self, load_repo: LoadRepository):
        self._load_repo = load_repo

    def execute(self, load_id: int) -> Load:
        load = self._load_repo.get(load_id)
        if load is None:
            raise ValueError(f"No load with id {load_id}")
        load.amount_paid = load.total
        load.payment_status = PaymentStatus.PAID
        return self._load_repo.update(load)