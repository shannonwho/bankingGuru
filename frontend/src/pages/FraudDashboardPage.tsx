import { useEffect, useState, useCallback } from "react";
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { RefreshCw } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { getFraudScores } from "@/lib/api";
import type { FraudSummary, ScoredTransaction } from "@/types";
import { Button } from "@/components/ui/button";

const RISK_COLORS: Record<string, string> = {
  HIGH: "#ef4444",
  MEDIUM: "#f97316",
  LOW: "#22c55e",
};

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border bg-card p-4">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="mt-1 text-2xl font-semibold">{value}</p>
    </div>
  );
}

function buildCategoryData(transactions: ScoredTransaction[]) {
  const totals: Record<string, { sum: number; count: number }> = {};
  for (const txn of transactions) {
    const cat = txn.merchant_category;
    if (!totals[cat]) totals[cat] = { sum: 0, count: 0 };
    totals[cat].sum += txn.fraud_score;
    totals[cat].count += 1;
  }
  return Object.entries(totals)
    .map(([category, { sum, count }]) => ({
      category,
      avg_score: Math.round((sum / count) * 100) / 100,
    }))
    .sort((a, b) => b.avg_score - a.avg_score)
    .slice(0, 5);
}

export function FraudDashboardPage() {
  const { customer } = useAuth();
  const [data, setData] = useState<FraudSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await getFraudScores({
        customer_name: customer?.customer_name,
      });
      setData(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load fraud data");
    } finally {
      setLoading(false);
    }
  }, [customer]);

  useEffect(() => {
    load();
  }, [load]);

  const highRisk = data?.scored_transactions.filter((t) => t.risk_level === "HIGH") ?? [];
  const pieData = data
    ? [
        { name: "High", value: data.high_risk_count },
        { name: "Medium", value: data.medium_risk_count },
        { name: "Low", value: data.low_risk_count },
      ]
    : [];
  const categoryData = data ? buildCategoryData(data.scored_transactions) : [];
  const pctHigh = data && data.total_scored > 0
    ? ((data.high_risk_count / data.total_scored) * 100).toFixed(1) + "%"
    : "—";

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Fraud Detection</h1>
        <Button variant="outline" size="sm" onClick={load} disabled={loading}>
          <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Stats row */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Total Scored" value={data?.total_scored ?? "—"} />
        <StatCard label="High Risk" value={data?.high_risk_count ?? "—"} />
        <StatCard
          label="Avg Fraud Score"
          value={data ? data.avg_fraud_score.toFixed(3) : "—"}
        />
        <StatCard label="% High Risk" value={pctHigh} />
      </div>

      {/* Charts row */}
      {data && data.total_scored > 0 && (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {/* Donut — risk distribution */}
          <div className="rounded-lg border bg-card p-4">
            <p className="mb-4 text-sm font-medium">Risk Distribution</p>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {pieData.map((entry) => (
                    <Cell
                      key={entry.name}
                      fill={
                        entry.name === "High"
                          ? RISK_COLORS.HIGH
                          : entry.name === "Medium"
                          ? RISK_COLORS.MEDIUM
                          : RISK_COLORS.LOW
                      }
                    />
                  ))}
                </Pie>
                <Tooltip formatter={(v) => [v, "Transactions"]} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Bar — top 5 categories by avg score */}
          <div className="rounded-lg border bg-card p-4">
            <p className="mb-4 text-sm font-medium">Top Categories by Avg Fraud Score</p>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={categoryData} layout="vertical" margin={{ left: 8, right: 24 }}>
                <XAxis type="number" domain={[0, 1]} tickFormatter={(v) => v.toFixed(1)} />
                <YAxis type="category" dataKey="category" width={110} tick={{ fontSize: 12 }} />
                <Tooltip formatter={(v: number | undefined) => [(v ?? 0).toFixed(3), "Avg Score"]} />
                <Bar dataKey="avg_score" fill="#6366f1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* High-risk transactions table */}
      <div className="rounded-lg border bg-card">
        <div className="border-b px-4 py-3">
          <p className="text-sm font-medium">
            High Risk Transactions{" "}
            <span className="text-muted-foreground">(score ≥ 0.60)</span>
          </p>
        </div>
        {highRisk.length === 0 ? (
          <p className="p-6 text-center text-sm text-muted-foreground">
            {loading ? "Loading…" : "No high-risk transactions found."}
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-xs text-muted-foreground">
                  <th className="px-4 py-2 font-medium">Merchant</th>
                  <th className="px-4 py-2 font-medium">Category</th>
                  <th className="px-4 py-2 font-medium text-right">Amount</th>
                  <th className="px-4 py-2 font-medium text-right">Score</th>
                  <th className="px-4 py-2 font-medium">Flags</th>
                </tr>
              </thead>
              <tbody>
                {highRisk.map((txn) => (
                  <tr key={txn.transaction_id} className="border-b last:border-0 hover:bg-muted/40">
                    <td className="px-4 py-2 font-medium">{txn.merchant_name}</td>
                    <td className="px-4 py-2 text-muted-foreground">{txn.merchant_category}</td>
                    <td className="px-4 py-2 text-right">
                      ${Math.abs(txn.amount).toLocaleString("en-US", { minimumFractionDigits: 2 })}
                    </td>
                    <td className="px-4 py-2 text-right">
                      <span className="inline-block rounded-full bg-red-100 px-2 py-0.5 text-xs font-semibold text-red-700">
                        {txn.fraud_score.toFixed(2)}
                      </span>
                    </td>
                    <td className="px-4 py-2">
                      <ul className="space-y-0.5">
                        {txn.flags.map((f, i) => (
                          <li key={i} className="text-xs text-muted-foreground">
                            • {f}
                          </li>
                        ))}
                      </ul>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
