import { useState, useEffect, useCallback } from "react";
import { api } from "../offline/dataService";
import TopBar from "../components/TopBar";

const TABS = [
  { key: "requested", label: "Pending" },
  { key: "confirmed", label: "Confirmed" },
  { key: "collected", label: "In Collection" },
];

export default function PickupRequests() {
  const [tab, setTab] = useState("requested");
  const [requests, setRequests] = useState([]);
  const [itemClasses, setItemClasses] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [error, setError] = useState(null);

  const refresh = useCallback(() => {
    Promise.all([api.getPickupRequestsByStatus(tab), api.getItemClasses()])
      .then(([requestData, itemClassData]) => {
        setRequests(requestData);
        setItemClasses(itemClassData);
        setError(null);
      })
      .catch((e) => setError(e.message));
  }, [tab]);

  useEffect(() => { refresh(); setSelectedId(null); }, [refresh]);

  const selected = requests.find((r) => r.id === selectedId);

  function handleConfirm(e) {
    e.preventDefault();
    const form = new FormData(e.target);
    api.confirmPickupRequest(selectedId, form.get("scheduled_date"))
      .then(() => { setSelectedId(null); refresh(); })
      .catch((err) => setError(err.message));
  }

  function handleCollect(e) {
    e.preventDefault();
    const form = new FormData(e.target);
    api.collectPickupRequest(selectedId, {
      item_class_id: Number(form.get("item_class_id")),
      quantity: Number(form.get("quantity")),
      price_charged: form.get("price_charged") ? Number(form.get("price_charged")) : null,
      expected_pickup_date: form.get("expected_pickup_date") || null,
    })
      .then(() => { setSelectedId(null); refresh(); })
      .catch((err) => setError(err.message));
  }

  function handleCancel(id) {
    api.cancelPickupRequest(id).then(refresh).catch((err) => setError(err.message));
  }

  return (
    <div>
      <TopBar title="Pickup Requests" />
      {error && <p className="error">{error}</p>}

      <div className="tabs">
        {TABS.map((t) => (
          <button key={t.key} className={tab === t.key ? "active" : ""} onClick={() => setTab(t.key)}>
            {t.label} ({t.key === tab ? requests.length : ""})
          </button>
        ))}
      </div>

      <table>
        <thead><tr><th>Customer</th><th>Phone</th><th>Address</th><th>Requested</th><th>Scheduled</th><th></th></tr></thead>
        <tbody>
          {requests.map((r) => (
            <tr key={r.id} style={{ cursor: "pointer" }} onClick={() => setSelectedId(r.id)}>
              <td>{r.customer_name}</td>
              <td>{r.phone}</td>
              <td>{r.address}</td>
              <td>{new Date(r.requested_at).toLocaleDateString(undefined, { month: "short", day: "numeric" })}</td>
              <td>{r.scheduled_date ?? "--"}</td>
              <td onClick={(e) => e.stopPropagation()}>
                {tab !== "collected" && (
                  <button className="btn-secondary" onClick={() => handleCancel(r.id)}>Cancel</button>
                )}
              </td>
            </tr>
          ))}
          {requests.length === 0 && (
            <tr><td colSpan={6} style={{ textAlign: "center", color: "var(--ink-muted)" }}>No requests here right now.</td></tr>
          )}
        </tbody>
      </table>

      {selected && tab === "requested" && (
        <div className="panel" style={{ marginTop: "1.5rem" }}>
          <h2 style={{ margin: 0, border: "none", padding: 0 }}>Confirm Pickup Request</h2>
          <p className="topbar-subtitle">{selected.customer_name} &middot; {selected.phone} &middot; {selected.address}</p>
          {selected.notes && <p className="topbar-subtitle">Notes: {selected.notes}</p>}
          <form onSubmit={handleConfirm} style={{ marginTop: "1rem" }}>
            <input name="scheduled_date" type="date" required />
            <button type="submit">Confirm &amp; Schedule</button>
          </form>
        </div>
      )}

      {selected && tab === "confirmed" && (
        <div className="panel" style={{ marginTop: "1.5rem" }}>
          <h2 style={{ margin: 0, border: "none", padding: 0 }}>Collect Items</h2>
          <p className="topbar-subtitle">{selected.customer_name} &middot; scheduled {selected.scheduled_date}</p>
          <form onSubmit={handleCollect} style={{ marginTop: "1rem" }}>
            <select name="item_class_id" required>
              {itemClasses.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
            <input name="quantity" type="number" min="1" placeholder="Quantity" required />
            <input name="price_charged" type="number" min="0.01" step="0.01" placeholder="Price (optional)" />
            <input name="expected_pickup_date" type="date" placeholder="Expected pickup date" />
            <button type="submit">Mark Collected</button>
          </form>
        </div>
      )}
    </div>
  );
}