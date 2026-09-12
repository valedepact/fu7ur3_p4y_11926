import { useState, useEffect, useCallback } from "react";
import { dataService as api } from "../offline/dataService";
import { usePeriod } from "../hooks/usePeriod";
import PeriodTabs from "../components/PeriodTabs";

const STATUSES = ["dropped_off", "washing", "ready", "picked_up"];

export default function Loads() {
  const { period, setPeriod, customRange, setCustomRange, range } = usePeriod();
  const [loads, setLoads] = useState([]);
  const [itemClasses, setItemClasses] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [statusFilter, setStatusFilter] = useState("all");
  const [error, setError] = useState(null);

  const refresh = useCallback(() => {
    if (!range?.start || !range?.end) return;
    Promise.all([api.getLoads(range.start, range.end), api.getItemClasses(), api.getCustomers()])
      .then(([loadsData, itemClassData, customerData]) => {
        setLoads(loadsData);
        setItemClasses(itemClassData);
        setCustomers(customerData);
        setError(null);
      })
      .catch((e) => setError(e.message));
  }, [range?.start, range?.end]);

  useEffect(() => { refresh(); }, [refresh]);

  const itemClassName = (id) => itemClasses.find((c) => c.id === id)?.name ?? id;
  const customerName = (id) => customers.find((c) => c.id === id)?.name ?? id;
  const visibleLoads = statusFilter === "all" ? loads : loads.filter((l) => l.status === statusFilter);

  function handleSubmit(e) {
    e.preventDefault();
    const form = new FormData(e.target);
    api
      .createLoad({
        customer_name: form.get("customer_name"),
        item_class_id: Number(form.get("item_class_id")),
        quantity: Number(form.get("quantity")),
        price_charged: form.get("price_charged") ? Number(form.get("price_charged")) : null,
        expected_pickup_date: form.get("expected_pickup_date") || null,
      })
      .then(() => { e.target.reset(); refresh(); })
      .catch((err) => setError(err.message));
  }

  return (
    <div>
      <h1>Loads</h1>
      {error && <p className="error">{error}</p>}
      <PeriodTabs period={period} setPeriod={setPeriod} customRange={customRange} setCustomRange={setCustomRange} />

      <div className="tabs">
        <button className={statusFilter === "all" ? "active" : ""} onClick={() => setStatusFilter("all")}>all</button>
        {STATUSES.map((s) => (
          <button key={s} className={statusFilter === s ? "active" : ""} onClick={() => setStatusFilter(s)}>{s}</button>
        ))}
      </div>

      <table>
        <thead>
          <tr><th>Customer</th><th>Item</th><th>Qty</th><th>Total</th><th>Pickup by</th><th>Status</th><th>Payment</th></tr>
        </thead>
        <tbody>
          {visibleLoads.map((load) => (
            <tr key={load.id}>
              <td>{customerName(load.customer_id)}</td>
              <td>{itemClassName(load.item_class_id)}</td>
              <td>{load.quantity}</td>
              <td>{load.price_charged * load.quantity}</td>
              <td>{load.expected_pickup_date ?? "--"}</td>
              <td>
                <select value={load.status}
                        onChange={(e) => api.updateLoadStatus(load.id, e.target.value).then(refresh)}>
                  {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
              </td>
              <td>
                {load.payment_status === "owing"
                  ? <button onClick={() => api.markLoadPaid(load.id).then(refresh)}>Mark paid</button>
                  : "paid"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Log a load</h2>
      <form onSubmit={handleSubmit}>
        <input name="customer_name" placeholder="Customer name" required />
        <select name="item_class_id" required>
          {itemClasses.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <input name="quantity" type="number" min="1" placeholder="Quantity" required />
        <input name="price_charged" type="number" step="0.01" placeholder="Price (optional)" />
        <input name="expected_pickup_date" type="date" />
        <button type="submit">Log load</button>
      </form>
    </div>
  );
}