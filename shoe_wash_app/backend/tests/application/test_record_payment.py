from datetime import datetime

from domain import Load, LoadItem, PaymentStatus
from application import RecordPayment


def _make_load(load_repo, price=5000, quantity=2):
    return load_repo.add(Load(
        id=None, dropped_off_at=datetime.now(), customer_id=1,
        items=[LoadItem(id=None, item_class_id=1, quantity=quantity, price_charged=price)],
    ))


def test_partial_payment_sets_partial_status(load_repo):
    load = _make_load(load_repo)  # total = 10000
    updated = RecordPayment(load_repo).execute(load.id, 4000)
    assert updated.amount_paid == 4000
    assert updated.payment_status == PaymentStatus.PARTIAL


def test_full_payment_sets_paid_status(load_repo):
    load = _make_load(load_repo)  # total = 10000
    updated = RecordPayment(load_repo).execute(load.id, 10000)
    assert updated.payment_status == PaymentStatus.PAID


def test_payments_accumulate_across_calls(load_repo):
    load = _make_load(load_repo)  # total = 10000
    use_case = RecordPayment(load_repo)
    use_case.execute(load.id, 4000)
    updated = use_case.execute(load.id, 6000)
    assert updated.amount_paid == 10000
    assert updated.payment_status == PaymentStatus.PAID


def test_rejects_overpayment(load_repo):
    load = _make_load(load_repo)  # total = 10000
    import pytest
    with pytest.raises(ValueError):
        RecordPayment(load_repo).execute(load.id, 10001)