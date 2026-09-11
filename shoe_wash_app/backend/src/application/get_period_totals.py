from dataclasses import dataclass
from datetime import date

from .interfaces import LoadRepository, ExpenseRepository


@dataclass
class PeriodTotals:
    """Result of totalling a date range -- this is what the dashboard reads."""

    sales: float
    expenses: float

    @property
    def balance(self) -> float:
        return self.sales - self.expenses


class GetPeriodTotals:
    """Use case: powers Today / Week / Month / Custom by summing over any
    date range, income and expenses kept separate."""

    def __init__(self, load_repo: LoadRepository, expense_repo: ExpenseRepository):
        self._load_repo = load_repo
        self._expense_repo = expense_repo

    def execute(self, start: date, end: date) -> PeriodTotals:
        loads = self._load_repo.list_between(start, end)
        expenses = self._expense_repo.list_between(start, end)

        sales = sum(load.total for load in loads)
        total_expenses = sum(expense.amount for expense in expenses)

        return PeriodTotals(sales=sales, expenses=total_expenses)
