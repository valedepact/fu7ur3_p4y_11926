import { useState, useEffect } from "react";
import { dataService as api } from "../offline/dataService";

export default function Customers() {
  const [customers, setCustomers] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getCustomers().then(setCustomers).catch((e) => setError(e.message));
  }, []);

  return (
    <div>
      <h1>Customers</h1>
      {error && <p className="error">{error}</p>}
      <table>
        <thead><tr><th>Name</th><th>Phone</th></tr></thead>
        <tbody>
          {customers.map((c) => <tr key={c.id}><td>{c.name}</td><td>{c.phone ?? "--"}</td></tr>)}
        </tbody>
      </table>
    </div>
  );
}