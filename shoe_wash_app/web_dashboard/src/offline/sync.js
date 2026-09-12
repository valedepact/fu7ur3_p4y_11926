import { api } from "../api";
import { readPendingActions, removePendingAction } from "./db";

async function replay(action, payload) {
  switch (action) {
    case "createLoad": return api.createLoad(payload);
    case "createExpense": return api.createExpense(payload);
    case "updateLoadStatus": return api.updateLoadStatus(payload.load_id, payload.status);
    case "markLoadPaid": return api.markLoadPaid(payload.load_id);
    case "createItemClass": return api.createItemClass(payload);
    default: return null;
  }
}

let syncing = false;

export async function syncNow() {
  if (syncing) return;
  syncing = true;
  try {
    const pending = await readPendingActions();
    for (const { id, action, payload } of pending) {
      try {
        await replay(action, payload);
        await removePendingAction(id);
      } catch { break; } // still offline or rejected -- stop, retry later
    }
  } finally {
    syncing = false;
  }
}

export function startSyncListener() {
  window.addEventListener("online", syncNow);
  syncNow();
}