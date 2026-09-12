import { openDB } from "idb";

const DB_NAME = "shoe_wash_offline";
const DB_VERSION = 1;

export async function getDb() {
  return openDB(DB_NAME, DB_VERSION, {
    upgrade(db) {
      if (!db.objectStoreNames.contains("cache")) db.createObjectStore("cache");
      if (!db.objectStoreNames.contains("pending")) {
        db.createObjectStore("pending", { keyPath: "id", autoIncrement: true });
      }
    },
  });
}

export async function saveCache(key, value) {
  const db = await getDb();
  await db.put("cache", value, key);
}

export async function readCache(key) {
  const db = await getDb();
  return (await db.get("cache", key)) ?? [];
}

export async function queueAction(action, payload) {
  const db = await getDb();
  await db.add("pending", { action, payload });
}

export async function readPendingActions() {
  const db = await getDb();
  return db.getAll("pending");
}

export async function removePendingAction(id) {
  const db = await getDb();
  await db.delete("pending", id);
}