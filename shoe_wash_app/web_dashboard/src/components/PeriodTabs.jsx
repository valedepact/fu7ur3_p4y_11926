export default function PeriodTabs({ period, setPeriod, customRange, setCustomRange }) {
  return (
    <>
      <div className="tabs">
        {["today", "week", "month", "custom"].map((p) => (
          <button key={p} className={p === period ? "active" : ""} onClick={() => setPeriod(p)}>
            {p}
          </button>
        ))}
      </div>
      {period === "custom" && (
        <div className="custom-range">
          <input type="date" value={customRange.start}
                 onChange={(e) => setCustomRange({ ...customRange, start: e.target.value })} />
          <span>to</span>
          <input type="date" value={customRange.end}
                 onChange={(e) => setCustomRange({ ...customRange, end: e.target.value })} />
        </div>
      )}
    </>
  );
}