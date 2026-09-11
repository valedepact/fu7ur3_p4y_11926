import sqlite3
from datetime import date, datetime
from typing import List

from domain import Load
from application import LoadRepository


class SqliteLoadRepository(LoadRepository):
    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection

    def add(self, load: Load) -> Load:
        cursor = self._conn.execute(
            """INSERT INTO loads (date, customer_id, item_class_id, quantity, price_charged)
               VALUES (?, ?, ?, ?, ?)""",
            (
                load.date.isoformat(),
                load.customer_id,
                load.item_class_id,
                load.quantity,
                load.price_charged,
            ),
        )
        self._conn.commit()
        load.id = cursor.lastrowid
        return load

    def list_between(self, start: date, end: date) -> List[Load]:
        rows = self._conn.execute(
            """SELECT id, date, customer_id, item_class_id, quantity, price_charged
               FROM loads WHERE date BETWEEN ? AND ?""",
            (start.isoformat(), end.isoformat()),
        ).fetchall()
        return [
            Load(
                id=row[0],
                date=datetime.strptime(row[1], "%Y-%m-%d").date(),
                customer_id=row[2],
                item_class_id=row[3],
                quantity=row[4],
                price_charged=row[5],
            )
            for row in rows
        ]
