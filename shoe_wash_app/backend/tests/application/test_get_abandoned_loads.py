from datetime import date, datetime, timedelta

from domain import Load, LoadStatus, BusinessSettings
from application import GetAbandonedLoads


def test_flags_loads_past_the_abandonment_window(load_repo, settings_repo):
    settings_repo.update(BusinessSettings(daily_operating_minutes=600, abandonment_days=14))
    old_pickup = date.today() - timedelta(days=20)
    load_repo.add(Load(id=None, dropped_off_at=datetime.now(), customer_id=1, item_class_id=1,
                        quantity=1, price_charged=5000, expected_pickup_date=old_pickup,
                        status=LoadStatus.READY))

    result = GetAbandonedLoads(load_repo, settings_repo).execute()

    assert len(result) == 1


def test_does_not_flag_picked_up_loads(load_repo, settings_repo):
    settings_repo.update(BusinessSettings(daily_operating_minutes=600, abandonment_days=14))
    old_pickup = date.today() - timedelta(days=20)
    load_repo.add(Load(id=None, dropped_off_at=datetime.now(), customer_id=1, item_class_id=1,
                        quantity=1, price_charged=5000, expected_pickup_date=old_pickup,
                        status=LoadStatus.PICKED_UP))

    result = GetAbandonedLoads(load_repo, settings_repo).execute()

    assert result == []