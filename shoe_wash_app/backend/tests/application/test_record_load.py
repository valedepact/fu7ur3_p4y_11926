import pytest

from domain import BusinessSettings, Customer, ItemClass
from application import RecordLoad


def test_defaults_price_to_item_class_base_price(load_repo, item_class_repo, customer_repo, settings_repo, sneakers, customer):
    use_case = RecordLoad(load_repo, item_class_repo, customer_repo, settings_repo)
    result = use_case.execute(customer_id=customer.id, item_class_id=sneakers.id, quantity=2)
    assert result.load.price_charged == sneakers.base_price
    assert result.warnings == []


def test_overriding_price_is_respected(load_repo, item_class_repo, customer_repo, settings_repo, sneakers, customer):
    use_case = RecordLoad(load_repo, item_class_repo, customer_repo, settings_repo)
    result = use_case.execute(customer_id=customer.id, item_class_id=sneakers.id, quantity=1, price_charged=7000)
    assert result.load.price_charged == 7000


def test_unit_cost_is_snapshotted_from_item_class(load_repo, item_class_repo, customer_repo, settings_repo, sneakers, customer):
    use_case = RecordLoad(load_repo, item_class_repo, customer_repo, settings_repo)
    result = use_case.execute(customer_id=customer.id, item_class_id=sneakers.id, quantity=1)
    assert result.load.unit_cost == sneakers.unit_cost


def test_warns_when_daily_capacity_is_exceeded(load_repo, item_class_repo, customer_repo, settings_repo, customer):
    settings_repo.update(BusinessSettings(daily_operating_minutes=30, abandonment_days=14))
    slow_item = item_class_repo.add(ItemClass(id=None, name="leather", base_price=7000, unit_cost=2000, wash_minutes=40))
    use_case = RecordLoad(load_repo, item_class_repo, customer_repo, settings_repo)

    result = use_case.execute(customer_id=customer.id, item_class_id=slow_item.id, quantity=1)

    assert any("capacity" in w for w in result.warnings)


def test_warns_when_customer_exceeds_credit_limit(load_repo, item_class_repo, customer_repo, settings_repo, sneakers):
    limited_customer = customer_repo.add(Customer(id=None, name="Limited", credit_limit=1000))
    use_case = RecordLoad(load_repo, item_class_repo, customer_repo, settings_repo)

    result = use_case.execute(customer_id=limited_customer.id, item_class_id=sneakers.id, quantity=1)

    assert any("credit limit" in w for w in result.warnings)


def test_raises_for_unknown_item_class(load_repo, item_class_repo, customer_repo, settings_repo, customer):
    use_case = RecordLoad(load_repo, item_class_repo, customer_repo, settings_repo)
    with pytest.raises(ValueError):
        use_case.execute(customer_id=customer.id, item_class_id=999, quantity=1)