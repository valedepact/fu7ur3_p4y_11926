from datetime import date, datetime

from domain import Load, LoadItem
from application import GetProfitability


def test_profit_accounts_for_unit_cost(load_repo):
    load_repo.add(Load(
        id=None, dropped_off_at=datetime(2026, 9, 10), customer_id=1,
        items=[LoadItem(id=None, item_class_id=1, quantity=2, price_charged=5000, unit_cost=1500)],
    ))

    result = GetProfitability(load_repo).execute(date(2026, 9, 1), date(2026, 9, 30))

    assert result.total_revenue == 10000
    assert result.total_cost == 3000
    assert result.total_profit == 7000
    assert round(result.profit_margin_pct) == 70