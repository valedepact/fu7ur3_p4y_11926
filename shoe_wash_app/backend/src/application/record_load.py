from datetime import date, datetime
from typing import Optional

from domain import Load
from .interfaces import LoadRepository, ItemClassRepository


class RecordLoad:
    def __init__(self, load_repo: LoadRepository, item_class_repo: ItemClassRepository):
        self._load_repo = load_repo
        self._item_class_repo = item_class_repo

    def execute(
        self,
        customer_id: int,
        item_class_id: int,
        quantity: int,
        price_charged: Optional[float] = None,
        expected_pickup_date: Optional[date] = None,
        dropped_off_at: Optional[datetime] = None,
    ) -> Load:
        item_class = self._item_class_repo.get(item_class_id)
        if item_class is None:
            raise ValueError(f"No item class with id {item_class_id}")

        load = Load(
            id=None,
            dropped_off_at=dropped_off_at or datetime.now(),
            customer_id=customer_id,
            item_class_id=item_class_id,
            quantity=quantity,
            price_charged=price_charged if price_charged is not None else item_class.base_price,
            expected_pickup_date=expected_pickup_date,
        )
        return self._load_repo.add(load)