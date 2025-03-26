import { NextResponse } from "next/server";
import Database from "better-sqlite3";
import path from "path";

export async function GET() {
  try {
    // Initialize database connection
    const dbPath =
      process.env.NODE_ENV === "production"
        ? "/home/ec2-user/data/ballknower.db"
        : "/Users/jamesmoore/Documents/ballknower/cron/ballknower.db";

    const db = new Database(dbPath);

    // Try a simple query
    db.prepare("SELECT 1").get();
    db.close();

    return NextResponse.json({
      status: "connected",
      message: "Database connection successful",
    });
  } catch (error) {
    console.error("Database connection error:", error);
    return NextResponse.json(
      { status: "error", message: "Failed to connect to database" },
      { status: 500 }
    );
  }
}
