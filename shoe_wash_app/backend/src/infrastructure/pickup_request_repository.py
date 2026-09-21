from datetime import datetime
from typing import List, Optional

from domain import PickupRequest
from application import PickupRequestRepository
from .supabase_client import get_client


def _row_to_request(row: dict) -> PickupRequest:
    return PickupRequest(
        id=row["id"], customer_name=row["customer_name"], phone=row["phone"], address=row["address"],
        requested_at=datetime.fromisoformat(row["requested_at"]), status=row["status"],
        scheduled_date=(
            datetime.strptime(row["scheduled_date"], "%Y-%m-%d").date() if row["scheduled_date"] else None
        ),
        notes=row["notes"], collected_load_id=row["collected_load_id"],
    )


class SupabasePickupRequestRepository(PickupRequestRepository):
    def __init__(self):
        self._client = get_client()

    def add(self, request: PickupRequest) -> PickupRequest:
        result = self._client.table("pickup_requests").insert(
            {
                "customer_name": request.customer_name, "phone": request.phone, "address": request.address,
                "requested_at": request.requested_at.isoformat(), "status": request.status,
                "scheduled_date": request.scheduled_date.isoformat() if request.scheduled_date else None,
                "notes": request.notes, "collected_load_id": request.collected_load_id,
            }
        ).execute()
        row = result.data[0]
        request.id = row["id"]
        return request

    def get(self, request_id: int) -> Optional[PickupRequest]:
        result = self._client.table("pickup_requests").select("*").eq("id", request_id).execute()
        if not result.data:
            return None
        return _row_to_request(result.data[0])

    def update(self, request: PickupRequest) -> PickupRequest:
        self._client.table("pickup_requests").update(
            {
                "status": request.status,
                "scheduled_date": request.scheduled_date.isoformat() if request.scheduled_date else None,
                "collected_load_id": request.collected_load_id,
            }
        ).eq("id", request.id).execute()
        return request

    def list_by_status(self, status: str) -> List[PickupRequest]:
        result = self._client.table("pickup_requests").select("*").eq("status", status).execute()
        return [_row_to_request(row) for row in result.data]