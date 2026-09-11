from datetime import date
from typing import Optional

from domain import Expense
from .interfaces import ExpenseRepository


class RecordExpense:
    """Use case: log a new expense."""

    def __init__(self, expense_repo: ExpenseRepository):
        self._expense_repo = expense_repo

    def execute(
        self,
        category: str,
        amount: float,
        note: Optional[str] = None,
        on_date: Optional[date] = None,
    ) -> Expense:
        expense = Expense(
            id=None,
            date=on_date or date.today(),
            category=category,
            amount=amount,
            note=note,
        )
        return self._expense_repo.add(expense)
