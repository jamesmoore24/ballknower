"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  ArrowRight,
  TrendingUp,
  DollarSign,
  BarChart3,
  Shield,
  RefreshCw,
} from "lucide-react";
import { useEffect, useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { getDbConfig } from "@/lib/db-config";

const dummyData = [
  { date: "Jan", profit: 2400 },
  { date: "Feb", profit: 4200 },
  { date: "Mar", profit: 3800 },
  { date: "Apr", profit: 6200 },
  { date: "May", profit: 5800 },
  { date: "Jun", profit: 8400 },
];

const arbitrageData = [
  { time: "9AM", odds1: 2.1, odds2: 1.9 },
  { time: "10AM", odds1: 2.3, odds2: 1.7 },
  { time: "11AM", odds1: 2.0, odds2: 2.0 },
  { time: "12PM", odds1: 1.8, odds2: 2.2 },
  { time: "1PM", odds1: 2.4, odds2: 1.6 },
];

type Entry = {
  id: number;
  date: string;
  odds: number;
  team: string;
  platform: string;
  created_at: string;
};

export default function Home() {
  const [entries, setEntries] = useState<Entry[]>([]);
  const [loading, setLoading] = useState(true);
  const [dbStatus, setDbStatus] = useState<{
    status: string;
    message: string;
    details?: {
      sizeBytes: number;
      sizeMB: string;
      tableCount: number;
      lastUpdate: string;
      tables: Array<{ table_name: string; row_count: number }>;
    };
  } | null>(null);
  const [checkingDb, setCheckingDb] = useState(false);

  const checkDatabaseConnection = async () => {
    setCheckingDb(true);
    try {
      const res = await fetch("/api/health");
      const data = await res.json();
      setDbStatus(data);
    } catch (error) {
      setDbStatus({
        status: "error",
        message: "Failed to check database connection",
      });
    } finally {
      setCheckingDb(false);
    }
  };

  const fetchEntries = async () => {
    setLoading(true);
    try {
      console.log(`Config: ${getDbConfig().path}`);
      const res = await fetch("/api/entries");
      const data = await res.json();
      setEntries(data.entries);
    } catch (error) {
      console.error("Error fetching entries:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEntries();
  }, []);

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-primary/10 to-primary/5 z-0" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16 text-center relative z-10">
          <h1 className="text-5xl md:text-6xl font-bold text-primary mb-6">
            Make Smarter Bets with{" "}
            <span className="text-blue-600">BallKnower</span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8">
            Advanced analytics, real-time visualizations, and arbitrage
            opportunities. Open source and free forever.
          </p>
          <Button size="lg" className="bg-blue-600 hover:bg-blue-700">
            Start Analyzing <ArrowRight className="ml-2" />
          </Button>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16 bg-muted/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card className="p-6">
              <TrendingUp className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Advanced Analytics</h3>
              <p className="text-muted-foreground">
                Machine learning powered insights and predictions for better
                decision making.
              </p>
            </Card>
            <Card className="p-6">
              <DollarSign className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Arbitrage Finder</h3>
              <p className="text-muted-foreground">
                Automatically detect profitable arbitrage opportunities across
                platforms.
              </p>
            </Card>
            <Card className="p-6">
              <BarChart3 className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Visual Insights</h3>
              <p className="text-muted-foreground">
                Beautiful, interactive charts and visualizations of betting
                trends.
              </p>
            </Card>
          </div>
        </div>
      </div>

      {/* Entries Table Section */}
      <div className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-12">
            <div className="flex items-center gap-4">
              <h2 className="text-3xl font-bold text-center">Recent Entries</h2>
              <Button
                onClick={checkDatabaseConnection}
                variant="outline"
                size="sm"
                className="flex items-center gap-2"
                disabled={checkingDb}
              >
                <Shield
                  className={`h-4 w-4 ${checkingDb ? "animate-spin" : ""}`}
                />
                Check DB
              </Button>
              {dbStatus && (
                <div className="text-sm">
                  <span
                    className={`font-medium ${
                      dbStatus.status === "connected"
                        ? "text-green-600"
                        : "text-red-600"
                    }`}
                  >
                    {dbStatus.message}
                  </span>
                  {dbStatus.details && (
                    <div className="mt-1 text-muted-foreground">
                      <div>Size: {dbStatus.details.sizeMB} MB</div>
                      <div>Tables: {dbStatus.details.tableCount}</div>
                      <div>
                        Last Update:{" "}
                        {new Date(dbStatus.details.lastUpdate).toLocaleString()}
                      </div>
                      <div className="mt-1">
                        {dbStatus.details.tables.map((table) => (
                          <div key={table.table_name} className="text-xs">
                            {table.table_name}: {table.row_count} rows
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
            <Button
              onClick={fetchEntries}
              variant="outline"
              size="sm"
              className="flex items-center gap-2"
              disabled={loading}
            >
              <RefreshCw
                className={`h-4 w-4 ${loading ? "animate-spin" : ""}`}
              />
              Refresh
            </Button>
          </div>
          <Card className="p-6">
            {loading ? (
              <div className="text-center py-4">Loading entries...</div>
            ) : entries.length === 0 ? (
              <div className="text-center py-4">No entries found</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Date</TableHead>
                    <TableHead>Team</TableHead>
                    <TableHead>Odds</TableHead>
                    <TableHead>Platform</TableHead>
                    <TableHead>Created At</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {entries.map((entry) => (
                    <TableRow key={entry.id}>
                      <TableCell>{entry.date}</TableCell>
                      <TableCell>{entry.team}</TableCell>
                      <TableCell>{entry.odds}</TableCell>
                      <TableCell>{entry.platform}</TableCell>
                      <TableCell>
                        {new Date(entry.created_at).toLocaleString()}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </Card>
        </div>
      </div>

      {/* Charts Section */}
      <div className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12">
            Data-Driven Decisions
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <Card className="p-6">
              <h3 className="text-xl font-semibold mb-4">Profit Tracking</h3>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={dummyData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="profit"
                      stroke="#2563eb"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </Card>
            <Card className="p-6">
              <h3 className="text-xl font-semibold mb-4">
                Arbitrage Opportunities
              </h3>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={arbitrageData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="odds1"
                      stroke="#2563eb"
                      strokeWidth={2}
                    />
                    <Line
                      type="monotone"
                      dataKey="odds2"
                      stroke="#16a34a"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </Card>
          </div>
        </div>
      </div>

      {/* Partners Section */}
      <div className="py-16 bg-muted/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-4">
            Supported Platforms
          </h2>
          <p className="text-center text-muted-foreground mb-12">
            We analyze odds from major betting platforms
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 items-center justify-items-center opacity-75">
            <img
              src="https://images.unsplash.com/photo-1669023414162-8b0573b9c6b2?w=200&h=100&fit=crop&q=80"
              alt="DraftKings"
              className="h-12 object-contain"
            />
            <img
              src="https://images.unsplash.com/photo-1669023414162-8b0573b9c6b2?w=200&h=100&fit=crop&q=80"
              alt="FanDuel"
              className="h-12 object-contain"
            />
            <img
              src="https://images.unsplash.com/photo-1669023414162-8b0573b9c6b2?w=200&h=100&fit=crop&q=80"
              alt="BetMGM"
              className="h-12 object-contain"
            />
            <img
              src="https://images.unsplash.com/photo-1669023414162-8b0573b9c6b2?w=200&h=100&fit=crop&q=80"
              alt="Caesars"
              className="h-12 object-contain"
            />
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="bg-muted/20 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-muted-foreground">
          <p className="mb-2">
            <Shield className="inline-block h-4 w-4 mr-1" />
            BallKnower is not affiliated with any betting platforms. We provide
            analytics and insights for informational purposes only.
          </p>
          <p>
            Please gamble responsibly. If you or someone you know has a gambling
            problem, crisis counseling and referral services can be accessed by
            calling 1-800-GAMBLER.
          </p>
        </div>
      </div>
    </div>
  );
}
