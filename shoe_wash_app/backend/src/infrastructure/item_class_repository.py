import sqlite3
from typing import List, Optional

from domain import ItemClass
from application import ItemClassRepository


class SqliteItemClassRepository(ItemClassRepository):
    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection

    def add(self, item_class: ItemClass) -> ItemClass:
        cursor = self._conn.execute(
            "INSERT INTO item_classes (name, base_price) VALUES (?, ?)",
            (item_class.name, item_class.base_price),
        )
        self._conn.commit()
        item_class.id = cursor.lastrowid
        return item_class

    def get(self, item_class_id: int) -> Optional[ItemClass]:
        row = self._conn.execute(
            "SELECT id, name, base_price FROM item_classes WHERE id = ?",
            (item_class_id,),
        ).fetchone()
        return ItemClass(*row) if row else None

    def list_all(self) -> List[ItemClass]:
        rows = self._conn.execute(
            "SELECT id, name, base_price FROM item_classes"
        ).fetchall()
        return [ItemClass(*row) for row in rows]
