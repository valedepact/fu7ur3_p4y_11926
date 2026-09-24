from dataclasses import dataclass
from datetime import date

from .interfaces import LoadRepository


@dataclass
class Profitability:
    total_revenue: float
    total_cost: float
    total_profit: float
    profit_margin_pct: float


class GetProfitability:
    """Use case: true profit per period, after item cost -- not just price charged."""

    def __init__(self, load_repo: LoadRepository):
        self._load_repo = load_repo

    def execute(self, start: date, end: date) -> Profitability:
        loads = self._load_repo.list_between(start, end)
        revenue = sum(l.total for l in loads)
        profit = sum(l.profit for l in loads)
        cost = revenue - profit
        margin = (profit / revenue * 100) if revenue else 0.0
        return Profitability(total_revenue=revenue, total_cost=cost, total_profit=profit, profit_margin_pct=margin)