import { useState, useEffect, useCallback } from "react";
import { api } from "../offline/dataService";
import { usePeriod } from "../hooks/usePeriod";
import PeriodTabs from "../components/PeriodTabs";
import TopBar from "../components/TopBar";

export default function Overview() {
  const { period, setPeriod, customRange, setCustomRange, range } = usePeriod();
  const [totals, setTotals] = useState({ sales: 0, expenses: 0, balance: 0 });
  const [loads, setLoads] = useState([]);
  const [outstanding, setOutstanding] = useState(0);
  const [error, setError] = useState(null);

  const refresh = useCallback(() => {
    if (!range?.start || !range?.end) return;
    Promise.all([
      api.getTotals(range.start, range.end),
      api.getLoads(range.start, range.end),
      api.getOutstandingBalance(),
    ])
      .then(([totalsData, loadsData, outstandingData]) => {
        setTotals(totalsData);
        setLoads(loadsData);
        setOutstanding(outstandingData.total_owed);
        setError(null);
      })
      .catch((e) => setError(e.message));
  }, [range?.start, range?.end]);

  useEffect(() => { refresh(); }, [refresh]);

  const inProgress = loads.filter((l) => !["picked_up", "delivered", "abandoned"].includes(l.status)).length;
  const readyForPickup = loads.filter((l) => l.status === "ready").length;

  const recentActivity = [...loads]
    .sort((a, b) => new Date(b.dropped_off_at) - new Date(a.dropped_off_at))
    .slice(0, 4);

  return (
    <div>
      <TopBar title="Overview" subtitle={range?.start && `${range.start} \u2192 ${range.end}`} />
      {error && <p className="error">{error}</p>}

      <PeriodTabs period={period} setPeriod={setPeriod} customRange={customRange} setCustomRange={setCustomRange} />

      <div className="stat-grid">
        <div className="stat-card success">
          <p className="stat-label">Income</p>
          <p className="stat-value">UGX {totals.sales.toLocaleString()}</p>
        </div>
        <div className="stat-card danger">
          <p className="stat-label">Expenses</p>
          <p className="stat-value">UGX {totals.expenses.toLocaleString()}</p>
        </div>
        <div className="stat-card neutral">
          <p className="stat-label">Net Balance</p>
          <p className="stat-value">UGX {totals.balance.toLocaleString()}</p>
        </div>
      </div>

      <div className="stat-grid">
        <div className="stat-card neutral">
          <p className="stat-label">Loads in Progress</p>
          <p className="stat-value">{inProgress}</p>
        </div>
        <div className="stat-card neutral">
          <p className="stat-label">Loads Ready for Pickup</p>
          <p className="stat-value">{readyForPickup}</p>
        </div>
        <div className="stat-card danger">
          <p className="stat-label">Outstanding Balance</p>
          <p className="stat-value">UGX {outstanding.toLocaleString()}</p>
        </div>
      </div>

      <div className="panel">
        <h2 style={{ margin: 0, border: "none", padding: 0 }}>Recent Activity</h2>
        <table style={{ marginTop: "1rem" }}>
          <tbody>
            {recentActivity.map((load) => (
              <tr key={load.id}>
                <td>Load logged &mdash; customer #{load.customer_id}</td>
                <td>{new Date(load.dropped_off_at).toLocaleDateString()}</td>
                <td style={{ textAlign: "right" }}>UGX {(load.price_charged * load.quantity).toLocaleString()}</td>
              </tr>
            ))}
            {recentActivity.length === 0 && (
              <tr><td>No activity yet in this period.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}