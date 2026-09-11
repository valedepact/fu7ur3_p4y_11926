from domain import ItemClass
from application import RecordLoad, RecordExpense, GetPeriodTotals, GetBalance
from infrastructure import (
    get_connection,
    SqliteCustomerRepository,
    SqliteItemClassRepository,
    SqliteLoadRepository,
    SqliteExpenseRepository,
)
from presentation import Cli


def seed_item_classes(item_class_repo):
    """Add starter item classes on first run, so the app is usable
    straight away without a setup step."""
    if item_class_repo.list_all():
        return
    defaults = [
        ItemClass(id=None, name="sneakers", base_price=5000),
        ItemClass(id=None, name="canvas", base_price=4000),
        ItemClass(id=None, name="leather", base_price=7000),
        ItemClass(id=None, name="sandals", base_price=3000),
    ]
    for item_class in defaults:
        item_class_repo.add(item_class)


def main():
    connection = get_connection("shoe_wash.db")

    customer_repo = SqliteCustomerRepository(connection)
    item_class_repo = SqliteItemClassRepository(connection)
    load_repo = SqliteLoadRepository(connection)
    expense_repo = SqliteExpenseRepository(connection)

    seed_item_classes(item_class_repo)

    record_load = RecordLoad(load_repo, item_class_repo)
    record_expense = RecordExpense(expense_repo)
    get_period_totals = GetPeriodTotals(load_repo, expense_repo)
    get_balance = GetBalance(get_period_totals)  # available for future use

    cli = Cli(record_load, record_expense, get_period_totals, customer_repo, item_class_repo)
    cli.run()


if __name__ == "__main__":
    main()
