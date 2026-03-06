import { useState } from "react";
import type { Dispute } from "@/types";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { DisputeStatusBadge } from "@/components/disputes/DisputeStatusBadge";
import { updateDispute } from "@/lib/api";
import { formatDateTime } from "@/lib/utils";

const TRANSITIONS: Record<string, string[]> = {
  submitted: ["under_review", "rejected"],
  under_review: ["resolved", "rejected"],
};

const statusLabel: Record<string, string> = {
  under_review: "Under Review",
  resolved: "Resolved",
  rejected: "Rejected",
};

interface Props {
  dispute: Dispute;
  onUpdated: (d: Dispute) => void;
}

export function DisputeDetail({ dispute, onUpdated }: Props) {
  const allowedNext = TRANSITIONS[dispute.status] ?? [];
  const [nextStatus, setNextStatus] = useState("");
  const [note, setNote] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const handleUpdate = async () => {
    if (!nextStatus) return;
    setSaving(true);
    setError("");
    try {
      const updated = await updateDispute(dispute.id, {
        status: nextStatus,
        resolution_note: note || undefined,
      });
      onUpdated(updated);
      setNextStatus("");
      setNote("");
    } catch (e: any) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-4 p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold capitalize">{dispute.reason.replace("_", " ")}</h3>
        <DisputeStatusBadge status={dispute.status} />
      </div>

      <div className="space-y-2 text-sm">
        <p><span className="text-muted-foreground">Transaction:</span> <span className="font-mono text-xs">{dispute.transaction_id}</span></p>
        <p><span className="text-muted-foreground">Filed:</span> {formatDateTime(dispute.filed_at)}</p>
        {dispute.resolved_at && (
          <p><span className="text-muted-foreground">Resolved:</span> {formatDateTime(dispute.resolved_at)}</p>
        )}
        <p><span className="text-muted-foreground">Description:</span></p>
        <p className="rounded-md bg-muted p-3">{dispute.description}</p>
        {dispute.resolution_note && (
          <>
            <p><span className="text-muted-foreground">Resolution Note:</span></p>
            <p className="rounded-md bg-muted p-3">{dispute.resolution_note}</p>
          </>
        )}
      </div>

      {allowedNext.length > 0 && (
        <>
          <Separator />
          <div className="space-y-3">
            <h4 className="text-sm font-medium">Update Status</h4>
            <Select value={nextStatus} onValueChange={setNextStatus}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Select status" />
              </SelectTrigger>
              <SelectContent>
                {allowedNext.map((s) => (
                  <SelectItem key={s} value={s}>{statusLabel[s] ?? s}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Textarea
              placeholder="Resolution note (optional)"
              value={note}
              onChange={(e) => setNote(e.target.value)}
              rows={3}
            />
            {error && <p className="text-sm text-destructive">{error}</p>}
            <Button onClick={handleUpdate} disabled={!nextStatus || saving} size="sm">
              {saving ? "Saving..." : "Update Dispute"}
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
