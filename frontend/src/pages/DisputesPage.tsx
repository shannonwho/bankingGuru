import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { DisputeList } from "@/components/disputes/DisputeList";
import { DisputeDetail } from "@/components/disputes/DisputeDetail";
import { DisputeForm } from "@/components/disputes/DisputeForm";
import { getDisputes } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import type { Dispute } from "@/types";

export function DisputesPage() {
  const { customer } = useAuth();
  const [disputes, setDisputes] = useState<Dispute[]>([]);
  const [selected, setSelected] = useState<Dispute | null>(null);
  const [statusFilter, setStatusFilter] = useState("");
  const [error, setError] = useState("");

  const load = () => {
    const params: Record<string, string> = {};
    if (customer) params.customer_name = customer.customer_name;
    if (statusFilter && statusFilter !== "all") params.status = statusFilter;
    getDisputes(params)
      .then(setDisputes)
      .catch((e) => setError(e.message));
  };

  useEffect(() => { load(); }, [statusFilter, customer]);

  const handleUpdated = (updated: Dispute) => {
    setDisputes((prev) => prev.map((d) => (d.id === updated.id ? updated : d)));
    setSelected(updated);
  };

  const handleCreated = (d: Dispute) => {
    setDisputes((prev) => [d, ...prev]);
    setSelected(d);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Disputes</h1>
        <DisputeForm onCreated={handleCreated} />
      </div>

      <div className="flex items-center gap-3">
        <label className="text-sm text-muted-foreground">Filter:</label>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-40"><SelectValue placeholder="All statuses" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All</SelectItem>
            <SelectItem value="open">Open</SelectItem>
            <SelectItem value="investigating">Investigating</SelectItem>
            <SelectItem value="resolved">Resolved</SelectItem>
            <SelectItem value="denied">Denied</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {error && <p className="text-destructive">{error}</p>}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[1fr_2fr]">
        <Card className="max-h-[calc(100vh-220px)] overflow-y-auto">
          <DisputeList disputes={disputes} selectedId={selected?.id ?? null} onSelect={setSelected} />
        </Card>

        <Card className="max-h-[calc(100vh-220px)] overflow-y-auto">
          {selected ? (
            <DisputeDetail dispute={selected} onUpdated={handleUpdated} />
          ) : (
            <p className="p-6 text-center text-sm text-muted-foreground">
              Select a dispute to view details
            </p>
          )}
        </Card>
      </div>
    </div>
  );
}
