from domain import PickupRequestStatus
from .interfaces import PickupRequestRepository


class CancelPickupRequest:
    def __init__(self, pickup_request_repo: PickupRequestRepository):
        self._repo = pickup_request_repo

    def execute(self, request_id: int):
        request = self._repo.get(request_id)
        if request is None:
            raise ValueError(f"No pickup request with id {request_id}")
        request.status = PickupRequestStatus.CANCELLED
        return self._repo.update(request)