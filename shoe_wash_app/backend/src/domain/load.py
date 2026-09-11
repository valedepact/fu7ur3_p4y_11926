from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Load:
    """One washing job: a customer's items, washed on a given date.

    price_charged is set at the time of the job and can differ from the
    item class's base_price -- some jobs cost more than others.
    """

    id: Optional[int]
    date: date
    customer_id: int
    item_class_id: int
    quantity: int
    price_charged: float

    @property
    def total(self) -> float:
        return self.price_charged * self.quantity
