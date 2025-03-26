import Database from "better-sqlite3";

// Use the BALLKNOWER_DB_PATH environment variable, default to 'ballknower.db' for local development
const dbPath = process.env.BALLKNOWER_DB_PATH || "ballknower.db";
const db = new Database(dbPath);

// Ensure the bets table exists (align with the schema used by update_bets.py)
db.exec(`
  CREATE TABLE IF NOT EXISTS bets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team TEXT,
    odds REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )
`);

export function getAllEntries() {
  return db.prepare("SELECT * FROM bets ORDER BY created_at DESC").all();
}

export function addEntry(entry: { team: string; odds: number }) {
  const stmt = db.prepare("INSERT INTO bets (team, odds) VALUES (?, ?)");
  return stmt.run(entry.team, entry.odds);
}

export default db;
