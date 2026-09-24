from datetime import datetime

import pytest

from domain import Load, LoadItem, LoadStatus, PaymentStatus, DeliveryMethod


def _load(items=None, **overrides):
    defaults = dict(id=1, dropped_off_at=datetime.now(), customer_id=1)
    defaults.update(overrides)
    if items is None:
        items = [LoadItem(id=1, item_class_id=1, quantity=2, price_charged=5000)]
    return Load(items=items, **defaults)


def test_total_sums_across_items():
    load = _load(items=[
        LoadItem(id=1, item_class_id=1, quantity=2, price_charged=5000),
        LoadItem(id=2, item_class_id=2, quantity=1, price_charged=7000),
    ])
    assert load.total == 17000


def test_profit_sums_across_items():
    load = _load(items=[
        LoadItem(id=1, item_class_id=1, quantity=2, price_charged=5000, unit_cost=1500),
    ])
    assert load.profit == 7000


def test_apply_payment_partial_sets_partial_status():
    load = _load()  # total = 10000
    load.apply_payment(4000)
    assert load.amount_paid == 4000
    assert load.payment_status == PaymentStatus.PARTIAL


def test_apply_payment_in_full_sets_paid_status():
    load = _load()  # total = 10000
    load.apply_payment(10000)
    assert load.payment_status == PaymentStatus.PAID


def test_apply_payment_rejects_overpayment():
    load = _load()  # total = 10000
    with pytest.raises(ValueError):
        load.apply_payment(10001)


def test_apply_payment_rejects_non_positive_amount():
    with pytest.raises(ValueError):
        _load().apply_payment(0)


def test_transition_dropped_off_to_washing_is_allowed():
    load = _load(status=LoadStatus.DROPPED_OFF)
    load.transition_to(LoadStatus.WASHING)
    assert load.status == LoadStatus.WASHING


def test_transition_cannot_skip_straight_to_picked_up():
    load = _load(status=LoadStatus.DROPPED_OFF)
    with pytest.raises(ValueError):
        load.transition_to(LoadStatus.PICKED_UP)


def test_transition_out_of_a_terminal_status_is_rejected():
    load = _load(status=LoadStatus.PICKED_UP)
    with pytest.raises(ValueError):
        load.transition_to(LoadStatus.WASHING)


def test_delivery_orders_must_use_delivered_not_picked_up():
    load = _load(status=LoadStatus.READY, delivery_method=DeliveryMethod.PICKUP_DELIVERY)
    with pytest.raises(ValueError):
        load.transition_to(LoadStatus.PICKED_UP)


def test_walk_in_orders_must_use_picked_up_not_delivered():
    load = _load(status=LoadStatus.READY, delivery_method=DeliveryMethod.WALK_IN)
    with pytest.raises(ValueError):
        load.transition_to(LoadStatus.DELIVERED)