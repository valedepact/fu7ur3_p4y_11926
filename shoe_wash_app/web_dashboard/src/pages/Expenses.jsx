import { useState, useEffect, useCallback } from "react";
import { dataService as api } from "../offline/dataService";
import { usePeriod } from "../hooks/usePeriod";
import PeriodTabs from "../components/PeriodTabs";
import { CATEGORY_LABELS } from "../labels";

const CATEGORIES = ["supplies", "utilities", "machine_upkeep", "other"];

export default function Expenses() {
  const { period, setPeriod, customRange, setCustomRange, range } = usePeriod();
  const [expenses, setExpenses] = useState([]);
  const [error, setError] = useState(null);

  const refresh = useCallback(() => {
    if (!range?.start || !range?.end) return;
    api.getExpenses(range.start, range.end)
      .then((data) => { setExpenses(data); setError(null); })
      .catch((e) => setError(e.message));
  }, [range?.start, range?.end]);

  useEffect(() => { refresh(); }, [refresh]);

  function handleSubmit(e) {
    e.preventDefault();
    const form = new FormData(e.target);
    api
      .createExpense({
        category: form.get("category"),
        amount: Number(form.get("amount")),
        note: form.get("note") || null,
      })
      .then(() => { e.target.reset(); refresh(); })
      .catch((err) => setError(err.message));
  }

  return (
    <div>
      <h1>Expenses</h1>
      {error && <p className="error">{error}</p>}
      <PeriodTabs period={period} setPeriod={setPeriod} customRange={customRange} setCustomRange={setCustomRange} />

      <table>
        <thead><tr><th>Date</th><th>Category</th><th>Amount</th><th>Note</th></tr></thead>
        <tbody>
          {expenses.map((exp) => (
            <tr key={exp.id}>
              <td>{exp.date}</td><td>{exp.category}</td><td>{exp.amount}</td><td>{exp.note ?? "--"}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Log an expense</h2>
      <form onSubmit={handleSubmit}>
        <select name="category" required>
          {CATEGORIES.map((c) => <option key={c} value={c}>{CATEGORY_LABELS[c]}</option>)}
        </select>
        <input name="amount" type="number" step="0.01" placeholder="Amount" required />
        <input name="note" placeholder="Note (optional)" />
        <button type="submit">Log expense</button>
      </form>
    </div>
  );
}