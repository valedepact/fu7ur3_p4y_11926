from datetime import datetime

from domain import Load
from application import GetOutstandingBalance


def test_sums_unpaid_balance_across_all_loads(load_repo):
    load_repo.add(Load(id=None, dropped_off_at=datetime.now(), customer_id=1, item_class_id=1,
                        quantity=1, price_charged=5000, amount_paid=2000))
    load_repo.add(Load(id=None, dropped_off_at=datetime.now(), customer_id=2, item_class_id=1,
                        quantity=1, price_charged=3000, amount_paid=3000))  # fully paid, excluded

    assert GetOutstandingBalance(load_repo).execute() == 3000