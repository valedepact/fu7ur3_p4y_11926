from typing import List, Optional

from domain import ItemClass
from application import ItemClassRepository
from .supabase_client import get_client


class SupabaseItemClassRepository(ItemClassRepository):
    def __init__(self):
        self._client = get_client()

    def add(self, item_class: ItemClass) -> ItemClass:
        result = self._client.table("item_classes").insert(
            {"name": item_class.name, "base_price": item_class.base_price}
        ).execute()
        row = result.data[0]
        item_class.id = row["id"]
        return item_class

    def get(self, item_class_id: int) -> Optional[ItemClass]:
        result = self._client.table("item_classes").select("*").eq("id", item_class_id).execute()
        if not result.data:
            return None
        row = result.data[0]
        return ItemClass(id=row["id"], name=row["name"], base_price=row["base_price"])

    def list_all(self) -> List[ItemClass]:
        result = self._client.table("item_classes").select("*").execute()
        return [ItemClass(id=row["id"], name=row["name"], base_price=row["base_price"]) for row in result.data]