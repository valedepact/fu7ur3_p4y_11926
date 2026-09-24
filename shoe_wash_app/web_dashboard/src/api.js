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
    createCustomer: (payload) =>
    request("/customers", { method: "POST", body: JSON.stringify(payload) }),
  getOutstandingBalance: () => request("/reports/outstanding-balance"),
  getProfitability: (start, end) => request(`/reports/profitability?start=${start}&end=${end}`),
  getPeakHours: (start, end) => request(`/reports/peak-hours?start=${start}&end=${end}`),
  getPopularItems: (start, end) => request(`/reports/popular-items?start=${start}&end=${end}`),
  getAbandonedLoads: () => request("/reports/abandoned"),
  getPickupRequests: (status) => request(`/pickup-requests?status=${status}`),
  confirmPickupRequest: (id, scheduled_date) =>
    request(`/pickup-requests/${id}/confirm`, { method: "PATCH", body: JSON.stringify({ scheduled_date }) }),
  collectPickupRequest: (id, payload) =>
    request(`/pickup-requests/${id}/collect`, { method: "PATCH", body: JSON.stringify(payload) }),
  cancelPickupRequest: (id) => request(`/pickup-requests/${id}/cancel`, { method: "PATCH" }),
  requestPickup: (payload) =>
    request("/pickup-requests", { method: "POST", body: JSON.stringify(payload) }),
  getSettings: () => request("/settings"),
  updateSettings: (payload) =>
    request("/settings", { method: "PUT", body: JSON.stringify(payload) }),
  recordPayment: (loadId, amount) =>
    request(`/loads/${loadId}/payments`, { method: "POST", body: JSON.stringify({ amount }) }),
    updateCustomer: (id, payload) =>
    request(`/customers/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  updateItemClass: (id, payload) =>
    request(`/item-classes/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  deleteItemClass: (id) =>
    request(`/item-classes/${id}`, { method: "DELETE" }),
  getPickupRequestsByStatus: (status) => 
    request(`/pickup-requests?status=${status}`),
};
