from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


class LoadStatus:
    DROPPED_OFF = "dropped_off"
    WASHING = "washing"
    READY = "ready"
    PICKED_UP = "picked_up"
    DELIVERED = "   delivered"
    ABANDONED = "abandoned"


class PaymentStatus:
    PAID = "paid"
    PARTIAL = "partial"
    OWING = "owing"

class DeliveryMethod:
    WALK_IN = "walk_in"
    PICKUP_DELIVERY = "pickup_delivery"


@dataclass
class Load:
    """One washing job: a customer's items, dropped off at a given moment."""

    id: Optional[int]
    dropped_off_at: datetime
    customer_id: int
    item_class_id: int
    quantity: int
    price_charged: float
    unit_cost: float = 0.0
    amount_paid: float = 0.0
    delivery_method: str = DeliveryMethod.WALK_IN
    pickup_address: Optional[str] = None
    delivery_address: Optional[str] = None
    status: str = LoadStatus.DROPPED_OFF
    expected_pickup_date: Optional[date] = None
    payment_status: str = PaymentStatus.OWING

    @property
    def total(self) -> float:
        return self.price_charged * self.quantity

    @property
    def profit(self) -> float:
        """Actual profit after the item's true cost, not just price charged."""
        return (self.price_charged - self.unit_cost) * self.quantity

    @property
    def date(self) -> date:
        return self.dropped_off_at.date()