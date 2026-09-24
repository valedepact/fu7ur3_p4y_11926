from domain import Load
from .interfaces import LoadRepository


class RecordPayment:
    """Use case: apply a payment, full or partial, to a load."""

    def __init__(self, load_repo: LoadRepository):
        self._load_repo = load_repo

    def execute(self, load_id: int, amount: float) -> Load:
        load = self._load_repo.get(load_id)
        if load is None:
            raise ValueError(f"No load with id {load_id}")

        load.apply_payment(amount)
        return self._load_repo.update(load)