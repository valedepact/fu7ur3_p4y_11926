from datetime import date

from .get_period_totals import GetPeriodTotals


class GetBalance:
    """Use case: sales minus expenses for a period, built on top of
    GetPeriodTotals rather than re-querying the repositories."""

    def __init__(self, get_period_totals: GetPeriodTotals):
        self._get_period_totals = get_period_totals

    def execute(self, start: date, end: date) -> float:
        return self._get_period_totals.execute(start, end).balance
