from datetime import datetime

from domain import Load


def test_total_is_price_times_quantity():
    load = Load(id=1, dropped_off_at=datetime.now(), customer_id=1, item_class_id=1,
                quantity=3, price_charged=5000)
    assert load.total == 15000


def test_profit_is_price_minus_cost_times_quantity():
    load = Load(id=1, dropped_off_at=datetime.now(), customer_id=1, item_class_id=1,
                quantity=2, price_charged=5000, unit_cost=1500)
    assert load.profit == 7000