import { useState, useEffect, useCallback, useMemo } from "react";
import { api } from "../offline/dataService";
import { usePeriod } from "../hooks/usePeriod";
import PeriodTabs from "../components/PeriodTabs";
import TopBar from "../components/TopBar";
import Pagination from "../components/Pagination";
import { CATEGORY_LABELS } from "../labels";

const CATEGORIES = ["supplies", "utilities", "machine_upkeep", "other"];
const PAGE_SIZE = 8;

export default function Expenses() {
  const { period, setPeriod, customRange, setCustomRange, range } = usePeriod();
  const [expenses, setExpenses] = useState([]);
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState(null);

  const refresh = useCallback(() => {
    if (!range?.start || !range?.end) return;
    api.getExpenses(range.start, range.end)
      .then((data) => { setExpenses(data); setError(null); })
      .catch((e) => setError(e.message));
  }, [range?.start, range?.end]);

  useEffect(() => { refresh(); }, [refresh]);
  useEffect(() => { setPage(1); }, [search, categoryFilter, range?.start, range?.end]);

  const visibleExpenses = useMemo(() => {
    return expenses.filter((exp) => {
      const matchesSearch = !search || (exp.note ?? "").toLowerCase().includes(search.toLowerCase());
      const matchesCategory = categoryFilter === "all" || exp.category === categoryFilter;
      return matchesSearch && matchesCategory;
    });
  }, [expenses, search, categoryFilter]);

  const pageItems = visibleExpenses.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  function handleSubmit(e) {
    e.preventDefault();
    const form = new FormData(e.target);
    api
      .createExpense({
        category: form.get("category"),
        amount: Number(form.get("amount")),
        note: form.get("note") || null,
      })
      .then(() => { e.target.reset(); setShowForm(false); refresh(); })
      .catch((err) => setError(err.message));
  }

  return (
    <div>
      <div className="panel-header">
        <TopBar title="Expenses" />
        <button className="btn-primary" onClick={() => setShowForm((s) => !s)}>
          {showForm ? "Close" : "+ Add Expense"}
        </button>
      </div>
      {error && <p className="error">{error}</p>}

      <PeriodTabs period={period} setPeriod={setPeriod} customRange={customRange} setCustomRange={setCustomRange} />

      <div className="toolbar">
        <input type="text" placeholder="Search description..." value={search} onChange={(e) => setSearch(e.target.value)} />
        <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
          <option value="all">All Categories</option>
          {CATEGORIES.map((c) => <option key={c} value={c}>{CATEGORY_LABELS[c]}</option>)}
        </select>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} style={{ marginBottom: "1.5rem" }}>
          <select name="category" required>
            {CATEGORIES.map((c) => <option key={c} value={c}>{CATEGORY_LABELS[c]}</option>)}
          </select>
          <input name="amount" type="number" step="0.01" placeholder="Amount (UGX)" required />
          <input name="note" placeholder="Description / Notes (optional)" />
          <button type="submit">Save Expense</button>
        </form>
      )}

      <table>
        <thead><tr><th>Date</th><th>Amount</th><th>Category</th><th>Description</th></tr></thead>
        <tbody>
          {pageItems.map((exp) => (
            <tr key={exp.id}>
              <td>{new Date(exp.date).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })}</td>
              <td>UGX {exp.amount.toLocaleString()}</td>
              <td>{CATEGORY_LABELS[exp.category]}</td>
              <td>{exp.note ?? "--"}</td>
            </tr>
          ))}
          {pageItems.length === 0 && (
            <tr><td colSpan={4} style={{ textAlign: "center", color: "var(--ink-muted)" }}>No expenses match your filters.</td></tr>
          )}
        </tbody>
      </table>

      <Pagination page={page} setPage={setPage} pageSize={PAGE_SIZE} total={visibleExpenses.length} />
    </div>
  );
}