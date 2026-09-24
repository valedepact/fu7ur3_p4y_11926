from datetime import date, datetime

import pytest

from domain import BusinessSettings, Customer, Expense, ItemClass, LoadItem


@pytest.mark.parametrize(
    "kwargs",
    [
        {"quantity": 0},
        {"quantity": -1},
        {"price_charged": 0},
        {"price_charged": -1},
        {"unit_cost": -1},
    ],
)
def test_load_item_rejects_invalid_values(kwargs):
    values = dict(id=None, item_class_id=1, quantity=1, price_charged=100)
    values.update(kwargs)
    with pytest.raises(ValueError):
        LoadItem(**values)


def test_item_class_rejects_invalid_values():
    with pytest.raises(ValueError):
        ItemClass(id=None, name="Shoes", base_price=0)
    with pytest.raises(ValueError):
        ItemClass(id=None, name="Shoes", base_price=100, unit_cost=-1)
    with pytest.raises(ValueError):
        ItemClass(id=None, name="Shoes", base_price=100, wash_minutes=0)


def test_expense_rejects_non_positive_amount():
    with pytest.raises(ValueError):
        Expense(id=None, date=date.today(), category="supplies", amount=0)


def test_customer_rejects_negative_credit_limit():
    with pytest.raises(ValueError):
        Customer(id=None, name="Customer", credit_limit=-1)


def test_business_settings_reject_invalid_limits():
    with pytest.raises(ValueError):
        BusinessSettings(daily_operating_minutes=0)
    with pytest.raises(ValueError):
        BusinessSettings(abandonment_days=0)
    with pytest.raises(ValueError):
        BusinessSettings(default_credit_limit=-1)