from datetime import date

from domain import PickupRequestStatus
from .interfaces import PickupRequestRepository


class ConfirmPickupRequest:
    """Use case: manager verifies the location and sets a pickup time."""

    def __init__(self, pickup_request_repo: PickupRequestRepository):
        self._repo = pickup_request_repo

    def execute(self, request_id: int, scheduled_date: date):
        request = self._repo.get(request_id)
        if request is None:
            raise ValueError(f"No pickup request with id {request_id}")
        request.status = PickupRequestStatus.CONFIRMED
        request.scheduled_date = scheduled_date
        return self._repo.update(request)