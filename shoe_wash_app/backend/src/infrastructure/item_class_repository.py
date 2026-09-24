from typing import List, Optional

from domain import ItemClass
from application import ItemClassRepository
from .supabase_client import get_client
from postgrest.exceptions import APIError

class SupabaseItemClassRepository(ItemClassRepository):
    def __init__(self):
        self._client = get_client()

    def add(self, item_class: ItemClass) -> ItemClass:
        result = self._client.table("item_classes").insert(
            {
                "name": item_class.name,
                "base_price": item_class.base_price,
                "unit_cost": item_class.unit_cost,
                "wash_minutes": item_class.wash_minutes,
            }
        ).execute()
        row = result.data[0]
        item_class.id = row["id"]
        return item_class

    def get(self, item_class_id: int) -> Optional[ItemClass]:
        result = self._client.table("item_classes").select("*").eq("id", item_class_id).execute()
        if not result.data:
            return None
        row = result.data[0]
        return ItemClass(
            id=row["id"], name=row["name"], base_price=row["base_price"],
            unit_cost=row["unit_cost"], wash_minutes=row["wash_minutes"],
        )

    def list_all(self) -> List[ItemClass]:
        rows = self._client.table("item_classes").select("*").execute().data
        return [
            ItemClass(
                id=row["id"], name=row["name"], base_price=row["base_price"],
                unit_cost=row["unit_cost"], wash_minutes=row["wash_minutes"],
            )
            for row in rows
        ]

    def update(self, item_class: ItemClass) -> ItemClass:
        self._client.table("item_classes").update(
            {"name": item_class.name, "base_price": item_class.base_price,
             "unit_cost": item_class.unit_cost, "wash_minutes": item_class.wash_minutes}
        ).eq("id", item_class.id).execute()
        return item_class

    def delete(self, item_class_id: int) -> None:
        try:
            self._client.table("item_classes").delete().eq("id", item_class_id).execute()
        except APIError as e:
            raise ValueError("Cannot delete an item class that already has loads recorded against it") from e
            