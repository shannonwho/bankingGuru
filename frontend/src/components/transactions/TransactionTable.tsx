import type { Transaction } from "@/types";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatCurrency, formatDateTime } from "@/lib/utils";
import { Flag } from "lucide-react";

interface Props {
  transactions: Transaction[];
  onSelect?: (t: Transaction) => void;
  /** When provided, a "Dispute" action button appears on each completed transaction row. */
  onDispute?: (t: Transaction) => void;
}

export function TransactionTable({ transactions, onSelect, onDispute }: Props) {
  const showActions = Boolean(onDispute);

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Date</TableHead>
          <TableHead>Merchant</TableHead>
          <TableHead>Category</TableHead>
          <TableHead>Type</TableHead>
          <TableHead>Status</TableHead>
          <TableHead className="text-right">Amount</TableHead>
          {showActions && <TableHead className="w-24" />}
        </TableRow>
      </TableHeader>
      <TableBody>
        {transactions.length === 0 ? (
          <TableRow>
            <TableCell colSpan={showActions ? 7 : 6} className="text-center text-muted-foreground">
              No transactions found.
            </TableCell>
          </TableRow>
        ) : (
          transactions.map((t) => (
            <TableRow
              key={t.id}
              className={onSelect ? "cursor-pointer" : ""}
              onClick={() => onSelect?.(t)}
            >
              <TableCell className="text-muted-foreground">{formatDateTime(t.transacted_at)}</TableCell>
              <TableCell className="font-medium">{t.merchant_name}</TableCell>
              <TableCell><Badge variant="secondary">{t.merchant_category}</Badge></TableCell>
              <TableCell>{t.transaction_type}</TableCell>
              <TableCell>
                <Badge variant={t.status === "completed" ? "success" : t.status === "pending" ? "warning" : "destructive"}>
                  {t.status}
                </Badge>
              </TableCell>
              <TableCell className={`text-right font-medium ${t.amount < 0 ? "text-red-600" : "text-emerald-600"}`}>
                {formatCurrency(t.amount)}
              </TableCell>
              {showActions && (
                <TableCell onClick={(e) => e.stopPropagation()}>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-7 px-2 text-xs text-muted-foreground hover:text-foreground"
                    onClick={() => onDispute?.(t)}
                    title="Dispute this charge"
                  >
                    <Flag className="h-3.5 w-3.5 mr-1" />
                    Dispute
                  </Button>
                </TableCell>
              )}
            </TableRow>
          ))
        )}
      </TableBody>
    </Table>
  );
}
