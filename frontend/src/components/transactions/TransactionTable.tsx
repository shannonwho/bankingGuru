import type { Transaction } from "@/types";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ShieldAlert } from "lucide-react";
import { formatCurrency, formatDateTime } from "@/lib/utils";

interface Props {
  transactions: Transaction[];
  onSelect?: (t: Transaction) => void;
  onDispute?: (t: Transaction) => void;
  disputedTxnIds?: Set<string>;
}

export function TransactionTable({ transactions, onSelect, onDispute, disputedTxnIds }: Props) {
  const showActions = !!onDispute;

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
          {showActions && <TableHead className="text-right" />}
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
          transactions.map((t) => {
            const alreadyDisputed = disputedTxnIds?.has(t.id);
            return (
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
                  <TableCell className="text-right">
                    {alreadyDisputed ? (
                      <Badge variant="secondary">Disputed</Badge>
                    ) : (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => { e.stopPropagation(); onDispute(t); }}
                      >
                        <ShieldAlert className="h-4 w-4 mr-1" />
                        Dispute
                      </Button>
                    )}
                  </TableCell>
                )}
              </TableRow>
            );
          })
        )}
      </TableBody>
    </Table>
  );
}
