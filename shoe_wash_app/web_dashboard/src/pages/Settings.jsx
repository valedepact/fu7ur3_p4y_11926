import { useState, useEffect } from "react";
import { api } from "../offline/dataService";
import TopBar from "../components/TopBar";

export default function Settings() {
  const [settings, setSettings] = useState(null);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getSettings().then(setSettings).catch((e) => setError(e.message));
  }, []);

  function handleSubmit(e) {
    e.preventDefault();
    const form = new FormData(e.target);
    api.updateSettings({
      daily_operating_minutes: Number(form.get("daily_operating_minutes")),
      abandonment_days: Number(form.get("abandonment_days")),
      default_credit_limit: Number(form.get("default_credit_limit")),
    })
      .then((data) => { setSettings(data); setSaved(true); setTimeout(() => setSaved(false), 2000); })
      .catch((err) => setError(err.message));
  }

  if (!settings) return <div><TopBar title="Business Settings" />{error && <p className="error">{error}</p>}</div>;

  return (
    <div>
      <TopBar title="Business Settings" />
      {error && <p className="error">{error}</p>}
      {saved && <p style={{ color: "var(--success)", fontSize: "0.9rem" }}>Saved.</p>}

      <div className="panel" style={{ maxWidth: 480 }}>
        <h2 style={{ margin: 0, border: "none", padding: 0 }}>Operational Rules</h2>
        <form onSubmit={handleSubmit} style={{ flexDirection: "column", alignItems: "stretch", marginTop: "1rem" }}>
          <label className="stat-label">Operating Minutes (per day)</label>
          <input name="daily_operating_minutes" type="number" min="1" defaultValue={settings.daily_operating_minutes} required />

          <label className="stat-label" style={{ marginTop: "0.75rem" }}>Default Credit Limit per Customer (UGX)</label>
          <input name="default_credit_limit" type="number" min="0" step="0.01" defaultValue={settings.default_credit_limit} required />

          <label className="stat-label" style={{ marginTop: "0.75rem" }}>Abandoned-Item Threshold (days)</label>
          <input name="abandonment_days" type="number" min="1" defaultValue={settings.abandonment_days} required />

          <button type="submit" style={{ marginTop: "1rem" }}>Save Changes</button>
        </form>
        <p className="topbar-subtitle" style={{ marginTop: "1rem" }}>
          These settings are used by the system for capacity checks and flagging abandoned items.
          The credit limit here is not yet auto-applied to new customers.
        </p>
      </div>
    </div>
  );
}