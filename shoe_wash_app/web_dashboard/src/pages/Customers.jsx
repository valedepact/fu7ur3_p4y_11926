import { useState, useEffect, useCallback, useMemo } from "react";
import { api } from "../offline/dataService";
import TopBar from "../components/TopBar";
import { STATUS_LABELS, STATUS_BADGE_CLASS, PAYMENT_LABELS, PAYMENT_BADGE_CLASS } from "../labels";

const TODAY = new Date().toISOString().slice(0, 10);
const EPOCH = "2000-01-01";

export default function Customers() {
  const [customers, setCustomers] = useState([]);
  const [loads, setLoads] = useState([]);
  const [itemClasses, setItemClasses] = useState([]);
  const [search, setSearch] = useState("");
  const [selectedId, setSelectedId] = useState(null);
  const [activeTab, setActiveTab] = useState("history");
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(false);
  const [error, setError] = useState(null);

  const refresh = useCallback(() => {
    Promise.all([api.getCustomers(), api.getLoads(EPOCH, TODAY), api.getItemClasses()])
      .then(([customerData, loadData, itemClassData]) => {
        setCustomers(customerData);
        setLoads(loadData);
        setItemClasses(itemClassData);
        setError(null);
      })
      .catch((e) => setError(e.message));
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  const itemClassName = (id) => itemClasses.find((c) => c.id === id)?.name ?? `#${id}`;

  const customerStats = useMemo(() => {
    const map = {};
    for (const l of loads) {
      if (!map[l.customer_id]) map[l.customer_id] = { totalLoads: 0, outstanding: 0 };
      map[l.customer_id].totalLoads += 1;
      const remaining = l.price_charged * l.quantity - l.amount_paid;
      if (remaining > 0) map[l.customer_id].outstanding += remaining;
    }
    return map;
  }, [loads]);

  const visibleCustomers = customers.filter((c) => {
    const q = search.toLowerCase();
    return !q || c.name.toLowerCase().includes(q) || (c.phone ?? "").toLowerCase().includes(q);
  });

  const selectedCustomer = customers.find((c) => c.id === selectedId);
  const selectedLoads = loads
    .filter((l) => l.customer_id === selectedId)
    .sort((a, b) => new Date(b.dropped_off_at) - new Date(a.dropped_off_at));

  function handleAddSubmit(e) {
    e.preventDefault();
    const form = new FormData(e.target);
    api
      .createCustomer({
        name: form.get("name"),
        phone: form.get("phone") || null,
        credit_limit: form.get("credit_limit") ? Number(form.get("credit_limit")) : null,
      })
      .then(() => { e.target.reset(); setShowForm(false); refresh(); })
      .catch((err) => setError(err.message));
  }

  function handleEditSubmit(e) {
    e.preventDefault();
    const form = new FormData(e.target);
    api
      .updateCustomer(selectedId, {
        name: form.get("name"),
        phone: form.get("phone") || null,
        credit_limit: form.get("credit_limit") ? Number(form.get("credit_limit")) : null,
      })
      .then(() => { setEditing(false); refresh(); })
      .catch((err) => setError(err.message));
  }

  return (
    <div>
      <div className="panel-header">
        <TopBar title="Customers" />
        <button className="btn-primary" onClick={() => setShowForm((s) => !s)}>
          {showForm ? "Close" : "+ Add Customer"}
        </button>
      </div>
      {error && <p className="error">{error}</p>}

      <div className="toolbar">
        <input type="text" placeholder="Search by name or phone..." value={search} onChange={(e) => setSearch(e.target.value)} />
      </div>

      {showForm && (
        <form onSubmit={handleAddSubmit} style={{ marginBottom: "1.5rem" }}>
          <input name="name" placeholder="Customer name" required />
          <input name="phone" placeholder="Phone (optional)" />
          <input name="credit_limit" type="number" step="0.01" placeholder="Credit limit (optional)" />
          <button type="submit">Save Customer</button>
        </form>
      )}

      <table>
        <thead><tr><th>Name</th><th>Phone</th><th>Total Loads</th><th>Outstanding</th></tr></thead>
        <tbody>
          {visibleCustomers.map((c) => {
            const stats = customerStats[c.id] ?? { totalLoads: 0, outstanding: 0 };
            return (
              <tr key={c.id} style={{ cursor: "pointer" }} onClick={() => { setSelectedId(c.id); setActiveTab("history"); setEditing(false); }}>
                <td>{c.name}</td>
                <td>{c.phone ?? "--"}</td>
                <td>{stats.totalLoads}</td>
                <td>UGX {stats.outstanding.toLocaleString()}</td>
              </tr>
            );
          })}
          {visibleCustomers.length === 0 && (
            <tr><td colSpan={4} style={{ textAlign: "center", color: "var(--ink-muted)" }}>No customers match your search.</td></tr>
          )}
        </tbody>
      </table>

      {selectedCustomer && (
        <div className="panel" style={{ marginTop: "1.5rem" }}>
          <div className="panel-header">
            <div>
              <h2 style={{ margin: 0, border: "none", padding: 0 }}>{selectedCustomer.name}</h2>
              <p className="topbar-subtitle">{selectedCustomer.phone ?? "No phone on file"}</p>
            </div>
            <button className="btn-secondary" onClick={() => setEditing((s) => !s)}>
              {editing ? "Cancel" : "Edit"}
            </button>
          </div>

          {editing ? (
            <form onSubmit={handleEditSubmit}>
              <input name="name" defaultValue={selectedCustomer.name} required />
              <input name="phone" defaultValue={selectedCustomer.phone ?? ""} placeholder="Phone" />
              <input name="credit_limit" type="number" step="0.01" defaultValue={selectedCustomer.credit_limit ?? ""} placeholder="Credit limit" />
              <button type="submit">Save Changes</button>
            </form>
          ) : (
            <>
              <div className="tabs">
                <button className={activeTab === "history" ? "active" : ""} onClick={() => setActiveTab("history")}>Load History</button>
                <button className={activeTab === "payments" ? "active" : ""} onClick={() => setActiveTab("payments")}>Payment History</button>
                <button className={activeTab === "credit" ? "active" : ""} onClick={() => setActiveTab("credit")}>Credit Limit</button>
              </div>

              {activeTab === "history" && (
                <table>
                  <thead><tr><th>Date</th><th>Items</th><th>Amount</th><th>Status</th></tr></thead>
                  <tbody>
                    {selectedLoads.map((l) => (
                      <tr key={l.id}>
                        <td>{new Date(l.dropped_off_at).toLocaleDateString(undefined, { month: "short", day: "numeric" })}</td>
                        <td>{l.quantity}x {itemClassName(l.item_class_id)}</td>
                        <td>UGX {(l.price_charged * l.quantity).toLocaleString()}</td>
                        <td><span className={`badge ${STATUS_BADGE_CLASS[l.status]}`}>{STATUS_LABELS[l.status]}</span></td>
                      </tr>
                    ))}
                    {selectedLoads.length === 0 && <tr><td colSpan={4}>No loads yet.</td></tr>}
                  </tbody>
                </table>
              )}

              {activeTab === "payments" && (
                <table>
                  <thead><tr><th>Date</th><th>Amount Paid</th><th>Total</th><th>Payment Status</th></tr></thead>
                  <tbody>
                    {selectedLoads.map((l) => (
                      <tr key={l.id}>
                        <td>{new Date(l.dropped_off_at).toLocaleDateString(undefined, { month: "short", day: "numeric" })}</td>
                        <td>UGX {l.amount_paid.toLocaleString()}</td>
                        <td>UGX {(l.price_charged * l.quantity).toLocaleString()}</td>
                        <td><span className={`badge ${PAYMENT_BADGE_CLASS[l.payment_status]}`}>{PAYMENT_LABELS[l.payment_status]}</span></td>
                      </tr>
                    ))}
                    {selectedLoads.length === 0 && <tr><td colSpan={4}>No payments yet.</td></tr>}
                  </tbody>
                </table>
              )}

              {activeTab === "credit" && (
                <div style={{ padding: "0.5rem 0" }}>
                  <p className="stat-label">Current credit limit</p>
                  <p className="stat-value">
                    {selectedCustomer.credit_limit != null ? `UGX ${selectedCustomer.credit_limit.toLocaleString()}` : "No limit set"}
                  </p>
                  <p className="topbar-subtitle">Click Edit above to change it.</p>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}