from domain import ItemClass
from application import RecordLoad, RecordExpense, GetPeriodTotals, UpdateLoadStatus, MarkLoadPaid
from infrastructure import (
    SupabaseCustomerRepository, SupabaseItemClassRepository,
    SupabaseLoadRepository, SupabaseExpenseRepository, SupabaseBusinessSettingsRepository,
)
from presentation import Cli


def seed_item_classes(item_class_repo):
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
    customer_repo = SupabaseCustomerRepository()
    item_class_repo = SupabaseItemClassRepository()
    load_repo = SupabaseLoadRepository()
    expense_repo = SupabaseExpenseRepository()

    seed_item_classes(item_class_repo)

    record_load = RecordLoad(load_repo, item_class_repo)
    record_expense = RecordExpense(expense_repo)
    get_period_totals = GetPeriodTotals(load_repo, expense_repo)
    update_load_status = UpdateLoadStatus(load_repo)
    mark_load_paid = MarkLoadPaid(load_repo)
    settings_repo = SupabaseBusinessSettingsRepository()
    record_load = RecordLoad(load_repo, item_class_repo, customer_repo, settings_repo)

    cli = Cli(record_load, record_expense, get_period_totals,update_load_status, mark_load_paid, customer_repo, item_class_repo)
    cli.run()


if __name__ == "__main__":
    main()