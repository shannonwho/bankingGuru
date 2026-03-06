import { useEffect, useState, useCallback } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { DisputeList } from "@/components/disputes/DisputeList";
import { DisputeForm } from "@/components/disputes/DisputeForm";
import { DisputeStatusBadge } from "@/components/disputes/DisputeStatusBadge";
import { getDisputes } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { formatDate } from "@/lib/utils";
import type { Dispute } from "@/types";

const statusOptions = [
  { value: "all", label: "All Statuses" },
  { value: "submitted", label: "Submitted" },
  { value: "under_review", label: "Under Review" },
  { value: "resolved", label: "Resolved" },
  { value: "rejected", label: "Rejected" },
];

export function MyDisputesPage() {
  const { customer } = useAuth();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [disputes, setDisputes] = useState<Dispute[]>([]);
  const [selected, setSelected] = useState<Dispute | null>(null);
  const [statusFilter, setStatusFilter] = useState("all");
  const [error, setError] = useState("");

  const prefillTxnId = searchParams.get("txn") ?? undefined;
  const [formOpen, setFormOpen] = useState(!!prefillTxnId);

  const load = useCallback(() => {
    if (!customer) return;
    const params: Record<string, string> = { customer_name: customer.customer_name };
    if (statusFilter !== "all") params.status = statusFilter;
    getDisputes(params)
      .then(setDisputes)
      .catch((e) => setError(e.message));
  }, [customer, statusFilter]);

  useEffect(() => { load(); }, [load]);

  const handleCreated = (d: Dispute) => {
    setDisputes((prev) => [d, ...prev]);
    setSelected(d);
    setFormOpen(false);
    navigate("/my-disputes", { replace: true });
  };

  const handleFormOpenChange = (open: boolean) => {
    setFormOpen(open);
    if (!open && prefillTxnId) {
      navigate("/my-disputes", { replace: true });
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">My Disputes</h1>
        <DisputeForm
          onCreated={handleCreated}
          prefillTransactionId={prefillTxnId}
          open={prefillTxnId ? formOpen : undefined}
          onOpenChange={prefillTxnId ? handleFormOpenChange : undefined}
        />
      </div>

      <div className="flex items-center gap-2">
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-48">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {statusOptions.map((o) => (
              <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {error && <p className="text-destructive">{error}</p>}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {disputes.length} dispute{disputes.length !== 1 && "s"}
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <DisputeList
              disputes={disputes}
              selectedId={selected?.id ?? null}
              onSelect={setSelected}
            />
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardContent className="p-6">
            {selected ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold capitalize">
                    {selected.reason.replace("_", " ")}
                  </h2>
                  <DisputeStatusBadge status={selected.status} />
                </div>
                <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
                  <div>
                    <dt className="text-muted-foreground">Transaction ID</dt>
                    <dd className="font-mono text-xs">{selected.transaction_id}</dd>
                  </div>
                  <div>
                    <dt className="text-muted-foreground">Filed</dt>
                    <dd>{formatDate(selected.filed_at)}</dd>
                  </div>
                  <div className="col-span-2">
                    <dt className="text-muted-foreground">Description</dt>
                    <dd>{selected.description}</dd>
                  </div>
                  {selected.resolution_note && (
                    <div className="col-span-2">
                      <dt className="text-muted-foreground">Resolution Note</dt>
                      <dd>{selected.resolution_note}</dd>
                    </div>
                  )}
                </dl>
              </div>
            ) : (
              <p className="text-center text-sm text-muted-foreground py-8">
                Select a dispute to view details
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
