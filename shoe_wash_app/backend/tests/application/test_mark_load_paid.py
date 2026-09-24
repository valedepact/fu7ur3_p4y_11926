from datetime import datetime

from domain import Load, LoadItem, PaymentStatus
from application import MarkLoadPaid


def test_marks_full_total_as_paid(load_repo):
    load = load_repo.add(Load(
        id=None, dropped_off_at=datetime.now(), customer_id=1,
        items=[LoadItem(id=None, item_class_id=1, quantity=3, price_charged=5000)],
    ))
    updated = MarkLoadPaid(load_repo).execute(load.id)
    assert updated.amount_paid == 15000
    assert updated.payment_status == PaymentStatus.PAID