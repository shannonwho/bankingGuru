import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { AccountList } from "@/components/accounts/AccountList";
import { getDashboardSummary, getAccounts } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { formatCurrency, formatDateTime } from "@/lib/utils";
import type { Account, DashboardSummary } from "@/types";
import { DollarSign, ArrowLeftRight, ShieldAlert, Users } from "lucide-react";

export function DashboardPage() {
  const { customer } = useAuth();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const params: Record<string, string> = {};
    if (customer) params.customer_name = customer.customer_name;
    Promise.all([getDashboardSummary(params), getAccounts(params)])
      .then(([s, a]) => {
        setSummary(s);
        setAccounts(a);
      })
      .catch((e) => setError(e.message));
  }, [customer]);

  if (error) return <p className="text-destructive">{error}</p>;
  if (!summary) return <p className="text-muted-foreground">Loading...</p>;

  const stats = [
    { label: "Total Balance", value: formatCurrency(summary.total_balance), icon: DollarSign },
    { label: "Accounts", value: summary.total_accounts, icon: Users },
    { label: "Transactions", value: summary.transaction_count.toLocaleString(), icon: ArrowLeftRight },
    { label: "Open Disputes", value: summary.open_disputes, icon: ShieldAlert },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map(({ label, value, icon: Icon }) => (
          <Card key={label}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">{label}</CardTitle>
              <Icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div>
        <h2 className="mb-3 text-lg font-semibold">Accounts</h2>
        <AccountList accounts={accounts} />
      </div>

      <div>
        <h2 className="mb-3 text-lg font-semibold">Recent Transactions</h2>
        <Card>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Merchant</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Amount</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {summary.recent_transactions.map((t) => (
                <TableRow key={t.id}>
                  <TableCell className="text-muted-foreground">{formatDateTime(t.transacted_at)}</TableCell>
                  <TableCell className="font-medium">{t.merchant_name}</TableCell>
                  <TableCell>
                    <Badge variant="secondary">{t.merchant_category}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={t.status === "completed" ? "success" : t.status === "pending" ? "warning" : "destructive"}>
                      {t.status}
                    </Badge>
                  </TableCell>
                  <TableCell className={`text-right font-medium ${t.amount < 0 ? "text-red-600" : "text-emerald-600"}`}>
                    {formatCurrency(t.amount)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      </div>
    </div>
  );
}
