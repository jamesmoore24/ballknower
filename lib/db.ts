import sqlite3 from "better-sqlite3";
import { getDbConfig } from "./db-config";

let db: any = null;

export function getDatabase() {
  if (db) return db;

  try {
    const config = getDbConfig();
    db = sqlite3(config.path, { readonly: config.readOnly });

    // Initialize schema
    if (!config.readOnly) {
      db.exec(`
        CREATE TABLE IF NOT EXISTS bets (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          team TEXT,
          odds REAL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
      `);
    }

    return db;
  } catch (error) {
    console.warn("Database initialization failed:", error);
    return null;
  }
}

export function getAllEntries() {
  const db = getDatabase();
  console.log("db", db);
  if (!db) return [];

  try {
    console.log("SELECTING ALL ENTRIES");
    return db.prepare("SELECT * FROM bets ORDER BY created_at DESC").all();
  } catch (error) {
    console.error("Error getting entries:", error);
    return [];
  }
}

export function addEntry(entry: { team: string; odds: number }) {
  const db = getDatabase();
  if (!db) return null;

  const stmt = db.prepare("INSERT INTO bets (team, odds) VALUES (?, ?)");
  return stmt.run(entry.team, entry.odds);
}

export default getDatabase();
