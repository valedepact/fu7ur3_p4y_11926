from datetime import datetime
from typing import Optional

from domain import PickupRequest
from .interfaces import PickupRequestRepository


class CreatePickupRequest:
    """Use case: a customer asks the shop to come collect their items."""

    def __init__(self, pickup_request_repo: PickupRequestRepository):
        self._repo = pickup_request_repo

    def execute(self, customer_name: str, phone: str, address: str, notes: Optional[str] = None) -> PickupRequest:
        request = PickupRequest(
            id=None, customer_name=customer_name, phone=phone, address=address,
            requested_at=datetime.now(), notes=notes,
        )
        return self._repo.add(request)