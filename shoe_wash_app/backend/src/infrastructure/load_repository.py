from datetime import date, datetime
from typing import List, Optional

from domain import Load
from application import LoadRepository
from .supabase_client import get_client


def _row_to_load(row: dict) -> Load:
    return Load(
        id=row["id"],
        dropped_off_at=datetime.fromisoformat(row["dropped_off_at"]),
        customer_id=row["customer_id"],
        item_class_id=row["item_class_id"],
        quantity=row["quantity"],
        price_charged=row["price_charged"],
        status=row["status"],
        expected_pickup_date=(
            datetime.strptime(row["expected_pickup_date"], "%Y-%m-%d").date()
            if row["expected_pickup_date"] else None
        ),
        payment_status=row["payment_status"],
    )


class SupabaseLoadRepository(LoadRepository):
    def __init__(self):
        self._client = get_client()

    def add(self, load: Load) -> Load:
        result = self._client.table("loads").insert(
            {
                "dropped_off_at": load.dropped_off_at.isoformat(),
                "customer_id": load.customer_id,
                "item_class_id": load.item_class_id,
                "quantity": load.quantity,
                "price_charged": load.price_charged,
                "status": load.status,
                "expected_pickup_date": (
                    load.expected_pickup_date.isoformat() if load.expected_pickup_date else None
                ),
                "payment_status": load.payment_status,
            }
        ).execute()
        row = result.data[0]
        load.id = row["id"]
        return load

    def get(self, load_id: int) -> Optional[Load]:
        result = self._client.table("loads").select("*").eq("id", load_id).execute()
        if not result.data:
            return None
        return _row_to_load(result.data[0])

    def update(self, load: Load) -> Load:
        self._client.table("loads").update(
            {
                "status": load.status,
                "payment_status": load.payment_status,
                "expected_pickup_date": (
                    load.expected_pickup_date.isoformat() if load.expected_pickup_date else None
                ),
            }
        ).eq("id", load.id).execute()
        return load

    def list_between(self, start: date, end: date) -> List[Load]:
        result = (
            self._client.table("loads")
            .select("*")
            .gte("dropped_off_at", start.isoformat())
            .lte("dropped_off_at", f"{end.isoformat()}T23:59:59")
            .execute()
        )
        return [_row_to_load(row) for row in result.data]