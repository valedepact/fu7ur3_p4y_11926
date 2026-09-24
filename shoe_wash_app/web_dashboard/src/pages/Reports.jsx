import { useState, useEffect, useCallback, useMemo } from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { api } from "../offline/dataService";
import { usePeriod } from "../hooks/usePeriod";
import PeriodTabs from "../components/PeriodTabs";
import TopBar from "../components/TopBar";

const COLORS = ["#2F5BEA", "#16A34A", "#D97706", "#EF4444", "#7C3AED", "#0891B2"];

export default function Reports() {
  const { period, setPeriod, customRange, setCustomRange, range } = usePeriod();
  const [tab, setTab] = useState("profitability");
  const [profitability, setProfitability] = useState(null);
  const [popularItems, setPopularItems] = useState([]);
  const [peakHours, setPeakHours] = useState({});
  const [loads, setLoads] = useState([]);
  const [itemClasses, setItemClasses] = useState([]);
  const [error, setError] = useState(null);

  const refresh = useCallback(() => {
    if (!range?.start || !range?.end) return;
    Promise.all([
      api.getProfitability(range.start, range.end),
      api.getPopularItems(range.start, range.end),
      api.getPeakHours(range.start, range.end),
      api.getLoads(range.start, range.end),
      api.getItemClasses(),
    ])
      .then(([p, popular, peak, loadData, itemClassData]) => {
        setProfitability(p);
        setPopularItems(popular);
        setPeakHours(peak);
        setLoads(loadData);
        setItemClasses(itemClassData);
        setError(null);
      })
      .catch((e) => setError(e.message));
  }, [range?.start, range?.end]);

  useEffect(() => { refresh(); }, [refresh]);

  const itemClassName = (id) => itemClasses.find((c) => c.id === id)?.name ?? `#${id}`;

  // Per-item-class profitability, computed client-side from raw loads --
  // there's no dedicated backend report for this breakdown yet.
  const byItemClass = useMemo(() => {
    const map = {};
    for (const l of loads) {
      for (const it of l.items) {
        if (!map[it.item_class_id]) {
          map[it.item_class_id] = { revenue: 0, cost: 0 };
        }
        map[it.item_class_id].revenue += it.price_charged * it.quantity;
        map[it.item_class_id].cost += it.unit_cost * it.quantity;
      }
    }
    return Object.entries(map).map(([id, v]) => ({
      id: Number(id),
      name: itemClassName(Number(id)),
      revenue: v.revenue,
      cost: v.cost,
      profit: v.revenue - v.cost,
      margin: v.revenue ? ((v.revenue - v.cost) / v.revenue) * 100 : 0,
    })).sort((a, b) => b.revenue - a.revenue);
  }, [loads, itemClasses]);
  
  const totalPopularRevenue = popularItems.reduce((sum, p) => sum + p.total_revenue, 0);
  const donutData = popularItems.map((p) => ({ name: itemClassName(p.item_class_id), value: p.total_revenue }));

  const peakHoursSorted = Object.entries(peakHours).sort((a, b) => Number(a[0]) - Number(b[0]));
  const maxPeak = Math.max(1, ...peakHoursSorted.map(([, c]) => c));

  return (
    <div>
      <TopBar title="Reports" subtitle={range?.start && `${range.start} \u2192 ${range.end}`} />
      {error && <p className="error">{error}</p>}

      <PeriodTabs period={period} setPeriod={setPeriod} customRange={customRange} setCustomRange={setCustomRange} />

      <div className="tabs">
        <button className={tab === "profitability" ? "active" : ""} onClick={() => setTab("profitability")}>Profitability</button>
        <button className={tab === "peak_hours" ? "active" : ""} onClick={() => setTab("peak_hours")}>Peak Hours</button>
        <button className={tab === "popular_items" ? "active" : ""} onClick={() => setTab("popular_items")}>Popular Items</button>
      </div>

      {tab === "profitability" && profitability && (
        <>
          <div className="stat-grid">
            <div className="stat-card neutral">
              <p className="stat-label">Total Revenue</p>
              <p className="stat-value">UGX {profitability.total_revenue.toLocaleString()}</p>
            </div>
            <div className="stat-card danger">
              <p className="stat-label">Total Costs</p>
              <p className="stat-value">UGX {profitability.total_cost.toLocaleString()}</p>
            </div>
            <div className="stat-card success">
              <p className="stat-label">Net Profit</p>
              <p className="stat-value">UGX {profitability.total_profit.toLocaleString()}</p>
            </div>
          </div>

          <div className="panel">
            <h2 style={{ margin: 0, border: "none", padding: 0 }}>Profitability by Item Class</h2>
            <table style={{ marginTop: "1rem" }}>
              <thead><tr><th>Item Class</th><th>Revenue</th><th>Cost</th><th>Profit</th><th>Margin</th></tr></thead>
              <tbody>
                {byItemClass.map((row) => (
                  <tr key={row.id}>
                    <td>{row.name}</td>
                    <td>{row.revenue.toLocaleString()}</td>
                    <td>{row.cost.toLocaleString()}</td>
                    <td>{row.profit.toLocaleString()}</td>
                    <td>{row.margin.toFixed(0)}%</td>
                  </tr>
                ))}
                {byItemClass.length === 0 && <tr><td colSpan={5}>No loads in this period.</td></tr>}
              </tbody>
            </table>
          </div>

          <div className="panel">
            <h2 style={{ margin: 0, border: "none", padding: 0 }}>Revenue Share by Item Class</h2>
            <div style={{ display: "flex", alignItems: "center", gap: "2rem", marginTop: "1rem" }}>
              <div style={{ width: 200, height: 200 }}>
                <ResponsiveContainer>
                  <PieChart>
                    <Pie data={donutData} dataKey="value" nameKey="name" innerRadius={55} outerRadius={90}>
                      {donutData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Pie>
                    <Tooltip formatter={(v) => `UGX ${v.toLocaleString()}`} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div>
                <p className="stat-label">Total</p>
                <p className="stat-value" style={{ marginBottom: "1rem" }}>UGX {totalPopularRevenue.toLocaleString()}</p>
                {donutData.map((d, i) => (
                  <div key={d.name} style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.85rem", marginBottom: "4px" }}>
                    <span style={{ width: 10, height: 10, borderRadius: "50%", background: COLORS[i % COLORS.length] }} />
                    {d.name} &mdash; {totalPopularRevenue ? ((d.value / totalPopularRevenue) * 100).toFixed(0) : 0}%
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}

      {tab === "peak_hours" && (
        <div className="panel">
          <h2 style={{ margin: 0, border: "none", padding: 0 }}>Drop-offs by Hour of Day</h2>
          <div style={{ marginTop: "1rem" }}>
            {peakHoursSorted.map(([hour, count]) => (
              <div key={hour} style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "6px" }}>
                <span style={{ width: 50, fontSize: "0.8rem", color: "var(--ink-soft)" }}>{hour}:00</span>
                <div style={{ flex: 1, background: "var(--bg)", borderRadius: 4, overflow: "hidden" }}>
                  <div style={{ width: `${(count / maxPeak) * 100}%`, background: "var(--primary)", height: 16 }} />
                </div>
                <span style={{ fontSize: "0.8rem", width: 24, textAlign: "right" }}>{count}</span>
              </div>
            ))}
            {peakHoursSorted.length === 0 && <p className="topbar-subtitle">No loads in this period.</p>}
          </div>
        </div>
      )}

      {tab === "popular_items" && (
        <table>
          <thead><tr><th>Item Class</th><th>Loads</th><th>Revenue</th></tr></thead>
          <tbody>
            {popularItems.map((p) => (
              <tr key={p.item_class_id}>
                <td>{itemClassName(p.item_class_id)}</td>
                <td>{p.load_count}</td>
                <td>UGX {p.total_revenue.toLocaleString()}</td>
              </tr>
            ))}
            {popularItems.length === 0 && <tr><td colSpan={3}>No loads in this period.</td></tr>}
          </tbody>
        </table>
      )}
    </div>
  );
}