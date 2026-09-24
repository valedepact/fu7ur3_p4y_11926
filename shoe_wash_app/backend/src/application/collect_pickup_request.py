from datetime import date
from typing import List, Optional

from domain import Customer, DeliveryMethod, PickupRequestStatus
from .interfaces import PickupRequestRepository, CustomerRepository
from .record_load import RecordLoad, RecordLoadResult, LoadItemInput


class CollectPickupRequest:
    def __init__(self, pickup_request_repo: PickupRequestRepository,
                 customer_repo: CustomerRepository, record_load: RecordLoad):
        self._repo = pickup_request_repo
        self._customer_repo = customer_repo
        self._record_load = record_load

    def execute(self, request_id: int, items: List[LoadItemInput],
                expected_pickup_date: Optional[date] = None) -> RecordLoadResult:
        request = self._repo.get(request_id)
        if request is None:
            raise ValueError(f"No pickup request with id {request_id}")

        customer = self._customer_repo.add(Customer(id=None, name=request.customer_name, phone=request.phone))

        result = self._record_load.execute(
            customer_id=customer.id,
            items=items,
            expected_pickup_date=expected_pickup_date,
            delivery_method=DeliveryMethod.PICKUP_DELIVERY,
            pickup_address=request.address,
            delivery_address=request.address,
        )

        request.status = PickupRequestStatus.COLLECTED
        request.collected_load_id = result.load.id
        self._repo.update(request)

        return result