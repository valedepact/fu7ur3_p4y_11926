from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional


class LoadStatus:
    DROPPED_OFF = "dropped_off"
    WASHING = "washing"
    READY = "ready"
    PICKED_UP = "picked_up"
    DELIVERED = "delivered"
    ABANDONED = "abandoned"


class PaymentStatus:
    PAID = "paid"
    PARTIAL = "partial"
    OWING = "owing"


class DeliveryMethod:
    WALK_IN = "walk_in"
    PICKUP_DELIVERY = "pickup_delivery"


_VALID_TRANSITIONS = {
    LoadStatus.DROPPED_OFF: {LoadStatus.WASHING, LoadStatus.ABANDONED},
    LoadStatus.WASHING: {LoadStatus.READY, LoadStatus.ABANDONED},
    LoadStatus.READY: {LoadStatus.PICKED_UP, LoadStatus.DELIVERED, LoadStatus.ABANDONED},
    LoadStatus.PICKED_UP: set(),
    LoadStatus.DELIVERED: set(),
    LoadStatus.ABANDONED: set(),
}


@dataclass
class LoadItem:
    """One item class within a load -- e.g. '2 sneakers' inside a basket
    that might also contain '1 leather'. Price and cost are snapshotted
    here, same reasoning as before: history must never change just
    because the item class's price list changes later."""

    id: Optional[int]
    item_class_id: int
    quantity: int
    price_charged: float
    unit_cost: float = 0.0

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.price_charged <= 0:
            raise ValueError("Price charged must be positive")
        if self.unit_cost < 0:
            raise ValueError("Unit cost cannot be negative")

    @property
    def total(self) -> float:
        return self.price_charged * self.quantity

    @property
    def profit(self) -> float:
        return (self.price_charged - self.unit_cost) * self.quantity


@dataclass
class Load:
    """One washing job: a customer's basket, dropped off at a given
    moment. Can contain several different item classes, but has a
    single status and a single payment for the whole basket."""

    id: Optional[int]
    dropped_off_at: datetime
    customer_id: int
    items: List[LoadItem] = field(default_factory=list)
    amount_paid: float = 0.0
    delivery_method: str = DeliveryMethod.WALK_IN
    pickup_address: Optional[str] = None
    delivery_address: Optional[str] = None
    status: str = LoadStatus.DROPPED_OFF
    expected_pickup_date: Optional[date] = None
    payment_status: str = PaymentStatus.OWING

    @property
    def total(self) -> float:
        return sum(item.total for item in self.items)

    @property
    def profit(self) -> float:
        return sum(item.profit for item in self.items)

    @property
    def date(self) -> date:
        return self.dropped_off_at.date()

    def apply_payment(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Payment amount must be positive")
        remaining = self.total - self.amount_paid
        if amount > remaining:
            raise ValueError(f"Payment of {amount} exceeds the remaining balance of {remaining}")
        self.amount_paid += amount
        if self.amount_paid >= self.total:
            self.payment_status = PaymentStatus.PAID
        elif self.amount_paid > 0:
            self.payment_status = PaymentStatus.PARTIAL
        else:
            self.payment_status = PaymentStatus.OWING

    def mark_paid_in_full(self) -> None:
        self.amount_paid = self.total
        self.payment_status = PaymentStatus.PAID

    def transition_to(self, new_status: str) -> None:
        allowed = _VALID_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise ValueError(f"Cannot move a load from '{self.status}' to '{new_status}'")
        if new_status == LoadStatus.PICKED_UP and self.delivery_method == DeliveryMethod.PICKUP_DELIVERY:
            raise ValueError("This is a delivery order -- use 'delivered', not 'picked_up'")
        if new_status == LoadStatus.DELIVERED and self.delivery_method == DeliveryMethod.WALK_IN:
            raise ValueError("This is a walk-in order -- use 'picked_up', not 'delivered'")
        self.status = new_status