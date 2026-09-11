import sqlite3
from datetime import date, datetime
from typing import List

from domain import Expense
from application import ExpenseRepository


class SqliteExpenseRepository(ExpenseRepository):
    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection

    def add(self, expense: Expense) -> Expense:
        cursor = self._conn.execute(
            "INSERT INTO expenses (date, category, amount, note) VALUES (?, ?, ?, ?)",
            (expense.date.isoformat(), expense.category, expense.amount, expense.note),
        )
        self._conn.commit()
        expense.id = cursor.lastrowid
        return expense

    def list_between(self, start: date, end: date) -> List[Expense]:
        rows = self._conn.execute(
            "SELECT id, date, category, amount, note FROM expenses WHERE date BETWEEN ? AND ?",
            (start.isoformat(), end.isoformat()),
        ).fetchall()
        return [
            Expense(
                id=row[0],
                date=datetime.strptime(row[1], "%Y-%m-%d").date(),
                category=row[2],
                amount=row[3],
                note=row[4],
            )
            for row in rows
        ]
