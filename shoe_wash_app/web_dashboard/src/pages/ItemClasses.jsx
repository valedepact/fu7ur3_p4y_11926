import { useState, useEffect, useCallback } from "react";
import { dataService as api } from "../offline/dataService";

export default function ItemClasses() {
  const [itemClasses, setItemClasses] = useState([]);
  const [error, setError] = useState(null);

  const refresh = useCallback(() => {
    api.getItemClasses().then(setItemClasses).catch((e) => setError(e.message));
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  function handleSubmit(e) {
    e.preventDefault();
    const form = new FormData(e.target);
    api
      .createItemClass({ name: form.get("name"), base_price: Number(form.get("base_price")) })
      .then(() => { e.target.reset(); refresh(); })
      .catch((err) => setError(err.message));
  }

  return (
    <div>
      <h1>Item classes</h1>
      {error && <p className="error">{error}</p>}
      <table>
        <thead><tr><th>Name</th><th>Base price</th></tr></thead>
        <tbody>
          {itemClasses.map((c) => <tr key={c.id}><td>{c.name}</td><td>{c.base_price}</td></tr>)}
        </tbody>
      </table>

      <h2>Add item class</h2>
      <form onSubmit={handleSubmit}>
        <input name="name" placeholder="Name (e.g. boots)" required />
        <input name="base_price" type="number" step="0.01" placeholder="Base price" required />
        <button type="submit">Add</button>
      </form>
    </div>
  );
}