from datetime import date
from typing import Optional

from domain import Load
from .interfaces import LoadRepository, ItemClassRepository


class RecordLoad:
    """Use case: log a new washing job.

    Depends only on the repository interfaces, never on SQLite directly --
    so infrastructure can change without this file changing.
    """

    def __init__(self, load_repo: LoadRepository, item_class_repo: ItemClassRepository):
        self._load_repo = load_repo
        self._item_class_repo = item_class_repo

    def execute(
        self,
        customer_id: int,
        item_class_id: int,
        quantity: int,
        price_charged: Optional[float] = None,
        on_date: Optional[date] = None,
    ) -> Load:
        item_class = self._item_class_repo.get(item_class_id)
        if item_class is None:
            raise ValueError(f"No item class with id {item_class_id}")

        load = Load(
            id=None,
            date=on_date or date.today(),
            customer_id=customer_id,
            item_class_id=item_class_id,
            quantity=quantity,
            price_charged=price_charged if price_charged is not None else item_class.base_price,
        )
        return self._load_repo.add(load)
