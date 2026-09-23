import { useState, useEffect, useCallback } from "react";
import { api } from "../offline/dataService";
import TopBar from "../components/TopBar";

export default function ItemClasses() {
  const [itemClasses, setItemClasses] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState(null);

  const refresh = useCallback(() => {
    api.getItemClasses().then(setItemClasses).catch((e) => setError(e.message));
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  const editingItem = itemClasses.find((c) => c.id === editingId);

  function handleSubmit(e) {
    e.preventDefault();
    const form = new FormData(e.target);
    const payload = {
      name: form.get("name"),
      base_price: Number(form.get("base_price")),
      unit_cost: Number(form.get("unit_cost") || 0),
      wash_minutes: Number(form.get("wash_minutes") || 30),
    };
    const call = editingId ? api.updateItemClass(editingId, payload) : api.createItemClass(payload);
    call
      .then(() => { e.target.reset(); setEditingId(null); refresh(); })
      .catch((err) => setError(err.message));
  }

  function handleDelete(id) {
    api.deleteItemClass(id).then(refresh).catch((err) => setError(err.message));
  }

  return (
    <div>
      <div className="panel-header">
        <TopBar title="Item Classes" />
      </div>
      {error && <p className="error">{error}</p>}

      <table>
        <thead><tr><th>Item Class</th><th>Base Price (UGX)</th><th>Unit Cost (UGX)</th><th>Wash Minutes</th><th></th></tr></thead>
        <tbody>
          {itemClasses.map((c) => (
            <tr key={c.id}>
              <td>{c.name}</td>
              <td>{c.base_price.toLocaleString()}</td>
              <td>{c.unit_cost.toLocaleString()}</td>
              <td>{c.wash_minutes}</td>
              <td style={{ textAlign: "right", whiteSpace: "nowrap" }}>
                <button className="btn-secondary" style={{ marginRight: "0.4rem" }} onClick={() => setEditingId(c.id)}>Edit</button>
                <button className="btn-secondary" onClick={() => handleDelete(c.id)}>Delete</button>
              </td>
            </tr>
          ))}
          {itemClasses.length === 0 && (
            <tr><td colSpan={5} style={{ textAlign: "center", color: "var(--ink-muted)" }}>No item classes yet.</td></tr>
          )}
        </tbody>
      </table>

      <h2>{editingId ? `Edit "${editingItem?.name}"` : "Add Item Class"}</h2>
      <form onSubmit={handleSubmit} key={editingId ?? "new"}>
        <input name="name" placeholder="Item class name (e.g. Boots)" defaultValue={editingItem?.name ?? ""} required />
        <input name="base_price" type="number" step="0.01" placeholder="Base price (UGX)" defaultValue={editingItem?.base_price ?? ""} required />
        <input name="unit_cost" type="number" step="0.01" placeholder="Unit cost (UGX)" defaultValue={editingItem?.unit_cost ?? ""} />
        <input name="wash_minutes" type="number" placeholder="Wash minutes" defaultValue={editingItem?.wash_minutes ?? ""} />
        {editingId && <button type="button" className="btn-secondary" onClick={() => setEditingId(null)}>Cancel</button>}
        <button type="submit">{editingId ? "Save Changes" : "Add Item Class"}</button>
      </form>
    </div>
  );
}