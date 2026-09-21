from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


class PickupRequestStatus:
    REQUESTED = "requested"
    CONFIRMED = "confirmed"
    COLLECTED = "collected"
    CANCELLED = "cancelled"


@dataclass
class PickupRequest:
    """A customer's request for the shop to come collect their items --
    exists before any Load does, since the shop doesn't know item class,
    quantity, or price until the items are actually in hand."""

    id: Optional[int]
    customer_name: str
    phone: str
    address: str
    requested_at: datetime
    status: str = PickupRequestStatus.REQUESTED
    scheduled_date: Optional[date] = None
    notes: Optional[str] = None
    collected_load_id: Optional[int] = None