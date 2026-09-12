const BASE_URL = import.meta.env.VITE_API_URL;

async function request(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Request failed");
  }
  return response.json();
}

export const api = {
  getCustomers: () => request("/customers"),
  getItemClasses: () => request("/item-classes"),
  getLoads: (start, end) => request(`/loads?start=${start}&end=${end}`),
  getTotals: (start, end) => request(`/totals?start=${start}&end=${end}`),
  createLoad: (payload) =>
    request("/loads", { method: "POST", body: JSON.stringify(payload) }),
  createExpense: (payload) =>
    request("/expenses", { method: "POST", body: JSON.stringify(payload) }),
  updateLoadStatus: (loadId, status) =>
    request(`/loads/${loadId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    }),
  markLoadPaid: (loadId) =>
    request(`/loads/${loadId}/pay`, { method: "PATCH" }),
    getExpenses: (start, end) => request(`/expenses?start=${start}&end=${end}`),
  createItemClass: (payload) =>
    request("/item-classes", { method: "POST", body: JSON.stringify(payload) }),
};
