import { useState, useEffect, useCallback } from "react";
import { dataService as api } from "../offline/dataService";
import { usePeriod } from "../hooks/usePeriod";
import PeriodTabs from "../components/PeriodTabs";

export default function Overview() {
  const { period, setPeriod, customRange, setCustomRange, range } = usePeriod();
  const [totals, setTotals] = useState({ sales: 0, expenses: 0, balance: 0 });
  const [loads, setLoads] = useState([]);
  const [error, setError] = useState(null);

  const refresh = useCallback(() => {
    if (!range?.start || !range?.end) return;
    Promise.all([api.getTotals(range.start, range.end), api.getLoads(range.start, range.end)])
      .then(([totalsData, loadsData]) => {
        setTotals(totalsData);
        setLoads(loadsData);
        setError(null);
      })
      .catch((e) => setError(e.message));
  }, [range?.start, range?.end]);

  useEffect(() => { refresh(); }, [refresh]);

  const today = new Date().toISOString().slice(0, 10);
  const pending = loads.filter((l) => l.status !== "picked_up").length;
  const overdue = loads.filter(
    (l) => l.expected_pickup_date && l.status !== "picked_up" && l.expected_pickup_date < today
  ).length;

  return (
    <div>
      <h1>Overview</h1>
      {error && <p className="error">{error}</p>}
      <PeriodTabs period={period} setPeriod={setPeriod} customRange={customRange} setCustomRange={setCustomRange} />

      <div className="totals">
        <div className="sales">Sales: {totals.sales}</div>
        <div className="expenses">Expenses: {totals.expenses}</div>
        <div className="balance">Balance: {totals.balance}</div>
      </div>

      <div className="totals">
        <div>Pending orders: {pending}</div>
        <div className="danger-text">Overdue pickups: {overdue}</div>
        <div>Total loads: {loads.length}</div>
      </div>
    </div>
  );
}