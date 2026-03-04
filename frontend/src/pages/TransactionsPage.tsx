import { useEffect, useState, useCallback } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { TransactionTable } from "@/components/transactions/TransactionTable";
import { TransactionFilters, type Filters } from "@/components/transactions/TransactionFilters";
import { getTransactions } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import type { Transaction } from "@/types";

const emptyFilters: Filters = {
  category: "",
  transaction_type: "",
  status: "",
  date_from: "",
  date_to: "",
};

export function TransactionsPage() {
  const { customer } = useAuth();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState<Filters>(emptyFilters);
  const [error, setError] = useState("");
  const perPage = 20;

  const load = useCallback(() => {
    const params: Record<string, string | number> = { page, per_page: perPage };
    if (customer) params.customer_name = customer.customer_name;
    if (filters.category && filters.category !== "all") params.category = filters.category;
    if (filters.transaction_type && filters.transaction_type !== "all") params.transaction_type = filters.transaction_type;
    if (filters.status && filters.status !== "all") params.status = filters.status;
    if (filters.date_from) params.date_from = filters.date_from;
    if (filters.date_to) params.date_to = filters.date_to;

    getTransactions(params)
      .then((r) => {
        setTransactions(r.items);
        setTotal(r.total);
      })
      .catch((e) => setError(e.message));
  }, [page, filters, customer]);

  useEffect(() => { load(); }, [load]);

  const totalPages = Math.ceil(total / perPage);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Transactions</h1>

      <TransactionFilters
        filters={filters}
        onChange={(f) => { setFilters(f); setPage(1); }}
        onReset={() => { setFilters(emptyFilters); setPage(1); }}
      />

      {error && <p className="text-destructive">{error}</p>}

      <Card>
        <TransactionTable transactions={transactions} />
      </Card>

      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {total} transaction{total !== 1 && "s"} found
        </p>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>
            Previous
          </Button>
          <span className="flex items-center text-sm text-muted-foreground">
            Page {page} of {totalPages || 1}
          </span>
          <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>
            Next
          </Button>
        </div>
      </div>
    </div>
  );
}
