import { NextResponse } from "next/server";
import { getAllEntries } from "@/lib/db";
import Database from "better-sqlite3";

export async function GET() {
  try {
    const dbPath =
      process.env.NODE_ENV === "production"
        ? "/home/ec2-user/data/ballknower.db"
        : "/Users/jamesmoore/Documents/ballknower/cron/ballknower.db";

    const db = new Database(dbPath);

    // Try a simple query
    const entries = db.prepare("SELECT * FROM bets").all();
    db.close();

    return NextResponse.json({ entries });
  } catch (error) {
    console.error("Error fetching entries:", error);
    return NextResponse.json(
      { error: "Failed to fetch entries" },
      { status: 500 }
    );
  }
}
