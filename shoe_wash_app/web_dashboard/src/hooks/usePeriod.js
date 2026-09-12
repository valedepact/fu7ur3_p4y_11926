import { useState } from "react";

function iso(d) { return d.toISOString().slice(0, 10); }

function rangeFor(period) {
  const today = new Date();
  if (period === "today") return { start: iso(today), end: iso(today) };
  if (period === "week") {
    const start = new Date(today);
    start.setDate(today.getDate() - today.getDay());
    return { start: iso(start), end: iso(today) };
  }
  if (period === "month") {
    const start = new Date(today.getFullYear(), today.getMonth(), 1);
    return { start: iso(start), end: iso(today) };
  }
  return null;
}

export function usePeriod(initial = "week") {
  const [period, setPeriod] = useState(initial);
  const [customRange, setCustomRange] = useState({ start: "", end: "" });
  const range = period === "custom" ? customRange : rangeFor(period);
  return { period, setPeriod, customRange, setCustomRange, range };
}