import sqlite3
from typing import List, Optional

from domain import Customer
from application import CustomerRepository


class SqliteCustomerRepository(CustomerRepository):
    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection

    def add(self, customer: Customer) -> Customer:
        cursor = self._conn.execute(
            "INSERT INTO customers (name, phone) VALUES (?, ?)",
            (customer.name, customer.phone),
        )
        self._conn.commit()
        customer.id = cursor.lastrowid
        return customer

    def get(self, customer_id: int) -> Optional[Customer]:
        row = self._conn.execute(
            "SELECT id, name, phone FROM customers WHERE id = ?", (customer_id,)
        ).fetchone()
        return Customer(*row) if row else None

    def list_all(self) -> List[Customer]:
        rows = self._conn.execute("SELECT id, name, phone FROM customers").fetchall()
        return [Customer(*row) for row in rows]
