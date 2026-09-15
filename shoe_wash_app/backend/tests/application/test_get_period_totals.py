from datetime import date, datetime

from domain import Load, Expense, ExpenseCategory
from application import GetPeriodTotals


def test_sums_sales_and_expenses_separately(load_repo, expense_repo):
    load_repo.add(Load(id=None, dropped_off_at=datetime(2026, 9, 10), customer_id=1, item_class_id=1,
                        quantity=2, price_charged=5000))
    expense_repo.add(Expense(id=None, date=date(2026, 9, 10), category=ExpenseCategory.SUPPLIES, amount=3000))

    totals = GetPeriodTotals(load_repo, expense_repo).execute(date(2026, 9, 1), date(2026, 9, 30))

    assert totals.sales == 10000
    assert totals.expenses == 3000
    assert totals.balance == 7000