from datetime import date, datetime, timedelta

from domain import Load, LoadItem, LoadStatus, BusinessSettings
from application import GetAbandonedLoads


def _load(status, pickup):
    return Load(
        id=None, dropped_off_at=datetime.now(), customer_id=1,
        items=[LoadItem(id=None, item_class_id=1, quantity=1, price_charged=5000)],
        expected_pickup_date=pickup, status=status,
    )


def test_flags_loads_past_the_abandonment_window(load_repo, settings_repo):
    settings_repo.update(BusinessSettings(daily_operating_minutes=600, abandonment_days=14))
    old_pickup = date.today() - timedelta(days=20)
    load_repo.add(_load(LoadStatus.READY, old_pickup))

    result = GetAbandonedLoads(load_repo, settings_repo).execute()
    assert len(result) == 1


def test_does_not_flag_picked_up_loads(load_repo, settings_repo):
    settings_repo.update(BusinessSettings(daily_operating_minutes=600, abandonment_days=14))
    old_pickup = date.today() - timedelta(days=20)
    load_repo.add(_load(LoadStatus.PICKED_UP, old_pickup))

    result = GetAbandonedLoads(load_repo, settings_repo).execute()
    assert result == []