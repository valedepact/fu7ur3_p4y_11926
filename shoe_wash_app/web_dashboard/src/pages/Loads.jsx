import { useState, useEffect, useCallback, useMemo } from "react";
import { api } from "../offline/dataService";
import { usePeriod } from "../hooks/usePeriod";
import PeriodTabs from "../components/PeriodTabs";
import TopBar from "../components/TopBar";
import Pagination from "../components/Pagination";
import { STATUS_LABELS, PAYMENT_LABELS, DELIVERY_LABELS, STATUS_BADGE_CLASS, PAYMENT_BADGE_CLASS } from "../labels";

const STATUSES = ["dropped_off", "washing", "ready", "picked_up", "delivered", "abandoned"];
const PAYMENT_STATUSES = ["owing", "partial", "paid"];
const DELIVERY_METHODS = ["walk_in", "pickup_delivery"];
const PAGE_SIZE = 8;

const loadTotal = (load) => load.items.reduce((sum, it) => sum + it.price_charged * it.quantity, 0);
const loadQuantity = (load) => load.items.reduce((sum, it) => sum + it.quantity, 0);
const loadSummary = (load, itemClasses) =>
  load.items
    .map((it) => `${it.quantity}x ${itemClasses.find((c) => c.id === it.item_class_id)?.name ?? `#${it.item_class_id}`}`)
    .join(", ");

export default function Loads() {
  const { period, setPeriod, customRange, setCustomRange, range } = usePeriod();
  const [loads, setLoads] = useState([]);
  const [itemClasses, setItemClasses] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [paymentFilter, setPaymentFilter] = useState("all");
  const [deliveryFilter, setDeliveryFilter] = useState("all");
  const [sortBy, setSortBy] = useState("newest");
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
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
  useEffect(() => { setPage(1); }, [search, statusFilter, paymentFilter, deliveryFilter, sortBy, range?.start, range?.end]);

  const customerName = (id) => customers.find((c) => c.id === id)?.name ?? `#${id}`;
  const customerPhone = (id) => customers.find((c) => c.id === id)?.phone ?? "";

  const visibleLoads = useMemo(() => {
    let result = loads.filter((l) => {
      const name = customerName(l.customer_id).toLowerCase();
      const phone = customerPhone(l.customer_id).toLowerCase();
      const q = search.toLowerCase();
      const matchesSearch = !q || name.includes(q) || phone.includes(q);
      const matchesStatus = statusFilter === "all" || l.status === statusFilter;
      const matchesPayment = paymentFilter === "all" || l.payment_status === paymentFilter;
      const matchesDelivery = deliveryFilter === "all" || l.delivery_method === deliveryFilter;
      return matchesSearch && matchesStatus && matchesPayment && matchesDelivery;
    });

    result = [...result].sort((a, b) => {
      if (sortBy === "newest") return new Date(b.dropped_off_at) - new Date(a.dropped_off_at);
      if (sortBy === "oldest") return new Date(a.dropped_off_at) - new Date(b.dropped_off_at);
      if (sortBy === "amount_high") return loadTotal(b) - loadTotal(a);
      if (sortBy === "amount_low") return loadTotal(a) - loadTotal(b);
      return 0;
    });

    return result;
  }, [loads, customers, search, statusFilter, paymentFilter, deliveryFilter, sortBy]);

  const pageItems = visibleLoads.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  function handleSubmit(e) {
    e.preventDefault();
    const form = new FormData(e.target);
    api
      .createLoad({
        customer_name: form.get("customer_name"),
        customer_phone: form.get("customer_phone") || null,
        items: [
          {
            item_class_id: Number(form.get("item_class_id")),
            quantity: Number(form.get("quantity")),
            price_charged: form.get("price_charged") ? Number(form.get("price_charged")) : null,
          },
        ],
        expected_pickup_date: form.get("expected_pickup_date") || null,
      })
      .then(() => { e.target.reset(); setShowForm(false); refresh(); })
      .catch((err) => setError(err.message));
  }

  return (
    <div>
      <div className="panel-header">
        <TopBar title="Loads" />
        <button className="btn-primary" onClick={() => setShowForm((s) => !s)}>
          {showForm ? "Close" : "+ Log Load"}
        </button>
      </div>
      {error && <p className="error">{error}</p>}

      <PeriodTabs period={period} setPeriod={setPeriod} customRange={customRange} setCustomRange={setCustomRange} />

      <div className="toolbar">
        <input type="text" placeholder="Search by customer name or phone..." value={search} onChange={(e) => setSearch(e.target.value)} />
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="all">All Statuses</option>
          {STATUSES.map((s) => <option key={s} value={s}>{STATUS_LABELS[s]}</option>)}
        </select>
        <select value={paymentFilter} onChange={(e) => setPaymentFilter(e.target.value)}>
          <option value="all">All Payment Status</option>
          {PAYMENT_STATUSES.map((s) => <option key={s} value={s}>{PAYMENT_LABELS[s]}</option>)}
        </select>
        <select value={deliveryFilter} onChange={(e) => setDeliveryFilter(e.target.value)}>
          <option value="all">All Delivery Methods</option>
          {DELIVERY_METHODS.map((d) => <option key={d} value={d}>{DELIVERY_LABELS[d]}</option>)}
        </select>
        <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
          <option value="newest">Sort: Newest first</option>
          <option value="oldest">Sort: Oldest first</option>
          <option value="amount_high">Sort: Amount high-low</option>
          <option value="amount_low">Sort: Amount low-high</option>
        </select>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} style={{ marginBottom: "1.5rem" }}>
          <input name="customer_name" placeholder="Customer name" required />
          <input name="customer_phone" placeholder="Phone (optional)" />
          <select name="item_class_id" required>
            {itemClasses.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <input name="quantity" type="number" min="1" placeholder="Quantity" required />
          <input name="price_charged" type="number" step="0.01" placeholder="Price (optional)" />
          <input name="expected_pickup_date" type="date" />
          <button type="submit">Save Load</button>
        </form>
      )}
      <p className="topbar-subtitle" style={{ marginTop: showForm ? "-1rem" : 0, marginBottom: "1.5rem" }}>
        {showForm && "This form logs one item type per load for now \u2014 tell me if you want multi-item entry here too."}
      </p>

      <table>
        <thead>
          <tr>
            <th>#</th><th>Customer</th><th>Items</th><th>Drop-off</th><th>Expected Pickup</th>
            <th>Status</th><th>Payment</th><th>Delivery</th>
          </tr>
        </thead>
        <tbody>
          {pageItems.map((load, i) => (
            <tr key={load.id}>
              <td>{String((page - 1) * PAGE_SIZE + i + 1).padStart(3, "0")}</td>
              <td>{customerName(load.customer_id)}</td>
              <td>{loadSummary(load, itemClasses)} &mdash; UGX {loadTotal(load).toLocaleString()}</td>
              <td>{new Date(load.dropped_off_at).toLocaleDateString(undefined, { month: "short", day: "numeric" })}</td>
              <td>{load.expected_pickup_date ? new Date(load.expected_pickup_date).toLocaleDateString(undefined, { month: "short", day: "numeric" }) : "--"}</td>
              <td>
                <select
                  value={load.status}
                  className={`badge ${STATUS_BADGE_CLASS[load.status]}`}
                  onChange={(e) => api.updateLoadStatus(load.id, e.target.value).then(refresh).catch((err) => setError(err.message))}
                >
                  {STATUSES.map((s) => <option key={s} value={s}>{STATUS_LABELS[s]}</option>)}
                </select>
              </td>
              <td><span className={`badge ${PAYMENT_BADGE_CLASS[load.payment_status]}`}>{PAYMENT_LABELS[load.payment_status]}</span></td>
              <td>{DELIVERY_LABELS[load.delivery_method]}</td>
            </tr>
          ))}
          {pageItems.length === 0 && (
            <tr><td colSpan={8} style={{ textAlign: "center", color: "var(--ink-muted)" }}>No loads match your filters.</td></tr>
          )}
        </tbody>
      </table>

      <Pagination page={page} setPage={setPage} pageSize={PAGE_SIZE} total={visibleLoads.length} />
    </div>
  );
}