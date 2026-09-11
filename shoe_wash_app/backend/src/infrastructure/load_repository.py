from datetime import date, datetime
from typing import List

from domain import Load
from application import LoadRepository
from .supabase_client import get_client


class SupabaseLoadRepository(LoadRepository):
    def __init__(self):
        self._client = get_client()

    def add(self, load: Load) -> Load:
        result = self._client.table("loads").insert(
            {
                "date": load.date.isoformat(),
                "customer_id": load.customer_id,
                "item_class_id": load.item_class_id,
                "quantity": load.quantity,
                "price_charged": load.price_charged,
            }
        ).execute()
        row = result.data[0]
        load.id = row["id"]
        return load

    def list_between(self, start: date, end: date) -> List[Load]:
        result = (
            self._client.table("loads")
            .select("*")
            .gte("date", start.isoformat())
            .lte("date", end.isoformat())
            .execute()
        )
        return [
            Load(
                id=row["id"],
                date=datetime.strptime(row["date"], "%Y-%m-%d").date(),
                customer_id=row["customer_id"],
                item_class_id=row["item_class_id"],
                quantity=row["quantity"],
                price_charged=row["price_charged"],
            )
            for row in result.data
        ]