from datetime import date, datetime
from typing import List, Optional

from domain import Load, LoadItem
from application import LoadRepository
from .supabase_client import get_client


def _row_to_item(row: dict) -> LoadItem:
    return LoadItem(
        id=row["id"], item_class_id=row["item_class_id"], quantity=row["quantity"],
        price_charged=row["price_charged"], unit_cost=row["unit_cost"],
    )


class SupabaseLoadRepository(LoadRepository):
    def __init__(self):
        self._client = get_client()

    def _load_from_row(self, row: dict) -> Load:
        item_rows = self._client.table("load_items").select("*").eq("load_id", row["id"]).execute().data
        return Load(
            id=row["id"],
            dropped_off_at=datetime.fromisoformat(row["dropped_off_at"]),
            customer_id=row["customer_id"],
            items=[_row_to_item(r) for r in item_rows],
            amount_paid=row["amount_paid"],
            delivery_method=row["delivery_method"],
            pickup_address=row["pickup_address"],
            delivery_address=row["delivery_address"],
            status=row["status"],
            expected_pickup_date=(
                datetime.strptime(row["expected_pickup_date"], "%Y-%m-%d").date()
                if row["expected_pickup_date"] else None
            ),
            payment_status=row["payment_status"],
        )

    def add(self, load: Load) -> Load:
        result = self._client.table("loads").insert(
            {
                "dropped_off_at": load.dropped_off_at.isoformat(),
                "customer_id": load.customer_id,
                "amount_paid": load.amount_paid,
                "status": load.status,
                "expected_pickup_date": (
                    load.expected_pickup_date.isoformat() if load.expected_pickup_date else None
                ),
                "payment_status": load.payment_status,
                "delivery_method": load.delivery_method,
                "pickup_address": load.pickup_address,
                "delivery_address": load.delivery_address,
            }
        ).execute()
        row = result.data[0]
        load.id = row["id"]

        item_rows = self._client.table("load_items").insert([
            {
                "load_id": load.id,
                "item_class_id": item.item_class_id,
                "quantity": item.quantity,
                "price_charged": item.price_charged,
                "unit_cost": item.unit_cost,
            }
            for item in load.items
        ]).execute().data
        for item, item_row in zip(load.items, item_rows):
            item.id = item_row["id"]

        return load

    def get(self, load_id: int) -> Optional[Load]:
        result = self._client.table("loads").select("*").eq("id", load_id).execute()
        if not result.data:
            return None
        return self._load_from_row(result.data[0])

    def update(self, load: Load) -> Load:
        # Items are immutable snapshots once created -- only load-level fields change here.
        self._client.table("loads").update(
            {
                "status": load.status,
                "payment_status": load.payment_status,
                "amount_paid": load.amount_paid,
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
        return [self._load_from_row(row) for row in result.data]