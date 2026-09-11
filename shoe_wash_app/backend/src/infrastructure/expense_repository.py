from datetime import date, datetime
from typing import List

from domain import Expense
from application import ExpenseRepository
from .supabase_client import get_client


class SupabaseExpenseRepository(ExpenseRepository):
    def __init__(self):
        self._client = get_client()

    def add(self, expense: Expense) -> Expense:
        result = self._client.table("expenses").insert(
            {
                "date": expense.date.isoformat(),
                "category": expense.category,
                "amount": expense.amount,
                "note": expense.note,
            }
        ).execute()
        row = result.data[0]
        expense.id = row["id"]
        return expense

    def list_between(self, start: date, end: date) -> List[Expense]:
        result = (
            self._client.table("expenses")
            .select("*")
            .gte("date", start.isoformat())
            .lte("date", end.isoformat())
            .execute()
        )
        return [
            Expense(
                id=row["id"],
                date=datetime.strptime(row["date"], "%Y-%m-%d").date(),
                category=row["category"],
                amount=row["amount"],
                note=row["note"],
            )
            for row in result.data
        ]