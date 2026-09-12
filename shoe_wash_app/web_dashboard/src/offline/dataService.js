import { api } from "../api";
import { saveCache, readCache, queueAction } from "./db";

export const dataService = {
  async getCustomers() {
    try {
      const data = await api.getCustomers();
      await saveCache("customers", data);
      return data;
    } catch { return readCache("customers"); }
  },

  async getItemClasses() {
    try {
      const data = await api.getItemClasses();
      await saveCache("item_classes", data);
      return data;
    } catch { return readCache("item_classes"); }
  },

  async getLoads(start, end) {
    const key = `loads_${start}_${end}`;
    try {
      const data = await api.getLoads(start, end);
      await saveCache(key, data);
      return data;
    } catch { return readCache(key); }
  },

  async getExpenses(start, end) {
    const key = `expenses_${start}_${end}`;
    try {
      const data = await api.getExpenses(start, end);
      await saveCache(key, data);
      return data;
    } catch { return readCache(key); }
  },

  async getTotals(start, end) {
    try {
      return await api.getTotals(start, end);
    } catch {
      const loads = await readCache(`loads_${start}_${end}`);
      const expenses = await readCache(`expenses_${start}_${end}`);
      const sales = loads.reduce((sum, l) => sum + l.price_charged * l.quantity, 0);
      const exp = expenses.reduce((sum, e) => sum + e.amount, 0);
      return { sales, expenses: exp, balance: sales - exp };
    }
  },

  async createLoad(payload) {
    try { return await api.createLoad(payload); }
    catch { await queueAction("createLoad", payload); return null; }
  },

  async createExpense(payload) {
    try { return await api.createExpense(payload); }
    catch { await queueAction("createExpense", payload); return null; }
  },

  async updateLoadStatus(loadId, status) {
    try { return await api.updateLoadStatus(loadId, status); }
    catch { await queueAction("updateLoadStatus", { load_id: loadId, status }); return null; }
  },

  async markLoadPaid(loadId) {
    try { return await api.markLoadPaid(loadId); }
    catch { await queueAction("markLoadPaid", { load_id: loadId }); return null; }
  },

  async createItemClass(payload) {
    try { return await api.createItemClass(payload); }
    catch { await queueAction("createItemClass", payload); return null; }
  },
};