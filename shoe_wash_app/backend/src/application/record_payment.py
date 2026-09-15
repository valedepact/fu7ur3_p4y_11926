from domain import Load, PaymentStatus
from .interfaces import LoadRepository


class RecordPayment:
    """Use case: apply a payment, full or partial, to a load."""

    def __init__(self, load_repo: LoadRepository):
        self._load_repo = load_repo

    def execute(self, load_id: int, amount: float) -> Load:
        load = self._load_repo.get(load_id)
        if load is None:
            raise ValueError(f"No load with id {load_id}")

        load.amount_paid += amount
        if load.amount_paid >= load.total:
            load.payment_status = PaymentStatus.PAID
        elif load.amount_paid > 0:
            load.payment_status = PaymentStatus.PARTIAL
        else:
            load.payment_status = PaymentStatus.OWING

        return self._load_repo.update(load)