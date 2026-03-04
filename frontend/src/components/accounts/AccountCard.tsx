import type { Account } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatCurrency } from "@/lib/utils";

const statusVariant: Record<string, "success" | "warning" | "destructive"> = {
  active: "success",
  frozen: "warning",
  closed: "destructive",
};

const typeLabel: Record<string, string> = {
  checking: "Checking",
  savings: "Savings",
  credit_card: "Credit Card",
};

export function AccountCard({ account }: { account: Account }) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div>
          <CardTitle className="text-base">{account.customer_name}</CardTitle>
          <p className="text-xs text-muted-foreground">{account.account_number}</p>
        </div>
        <Badge variant={statusVariant[account.status] ?? "secondary"}>
          {account.status}
        </Badge>
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline justify-between">
          <span className="text-2xl font-bold">{formatCurrency(account.balance)}</span>
          <span className="text-xs text-muted-foreground">
            {typeLabel[account.account_type] ?? account.account_type}
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
