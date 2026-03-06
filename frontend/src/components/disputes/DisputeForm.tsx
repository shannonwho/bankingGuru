import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogDescription,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { createDispute } from "@/lib/api";
import { formatCurrency, formatDateTime } from "@/lib/utils";
import type { Dispute, Transaction } from "@/types";
import { Plus, AlertTriangle } from "lucide-react";

const REASON_LABELS: Record<string, string> = {
  unauthorized: "Unauthorized charge",
  duplicate: "Duplicate charge",
  wrong_amount: "Wrong amount",
  not_received: "Item not received",
  other: "Other",
};

const DISPUTE_WINDOW_DAYS = 120;

function isWithinDisputeWindow(transactedAt: string): boolean {
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - DISPUTE_WINDOW_DAYS);
  return new Date(transactedAt) >= cutoff;
}

interface Props {
  /** When provided, the form is pre-filled from the transaction and skips manual UUID entry. */
  transaction?: Transaction;
  onCreated: (d: Dispute) => void;
  /** Controlled open state — used when triggered programmatically (e.g. from a table row). */
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}

export function DisputeForm({ transaction, onCreated, open: controlledOpen, onOpenChange }: Props) {
  const isControlled = controlledOpen !== undefined;
  const [internalOpen, setInternalOpen] = useState(false);
  const open = isControlled ? controlledOpen : internalOpen;

  const setOpen = (value: boolean) => {
    if (isControlled) {
      onOpenChange?.(value);
    } else {
      setInternalOpen(value);
    }
  };

  const [transactionId, setTransactionId] = useState(transaction?.id ?? "");
  const [reason, setReason] = useState("");
  const [description, setDescription] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  // Reset form state when the dialog opens with a new transaction
  useEffect(() => {
    if (open) {
      setTransactionId(transaction?.id ?? "");
      setReason("");
      setDescription("");
      setError("");
    }
  }, [open, transaction?.id]);

  const windowExpired = transaction ? !isWithinDisputeWindow(transaction.transacted_at) : false;

  const handleSubmit = async () => {
    if (!transactionId || !reason || !description) return;
    setSaving(true);
    setError("");
    try {
      const dispute = await createDispute({ transaction_id: transactionId, reason, description });
      onCreated(dispute);
      setOpen(false);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  };

  const content = (
    <DialogContent>
      <DialogHeader>
        <DialogTitle>File a Dispute</DialogTitle>
        <DialogDescription>
          {transaction
            ? "Review the transaction details and select a reason for the dispute."
            : "Enter the transaction ID and reason for the dispute."}
        </DialogDescription>
      </DialogHeader>

      <div className="space-y-4">
        {/* Transaction summary (pre-filled) */}
        {transaction ? (
          <div className="rounded-md border bg-muted/40 p-3 space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">{transaction.merchant_name}</span>
              <span className={`text-sm font-semibold ${transaction.amount < 0 ? "text-red-600" : "text-emerald-600"}`}>
                {formatCurrency(transaction.amount)}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="secondary">{transaction.merchant_category}</Badge>
              <span className="text-xs text-muted-foreground">{formatDateTime(transaction.transacted_at)}</span>
            </div>
            {windowExpired && (
              <div className="flex items-center gap-1.5 rounded-md bg-destructive/10 px-2 py-1.5 text-xs text-destructive">
                <AlertTriangle className="h-3.5 w-3.5" />
                Dispute window expired — this transaction is older than {DISPUTE_WINDOW_DAYS} days.
              </div>
            )}
          </div>
        ) : (
          <div>
            <label className="mb-1 block text-sm font-medium">Transaction ID</label>
            <Input
              placeholder="Paste transaction UUID"
              value={transactionId}
              onChange={(e) => setTransactionId(e.target.value)}
            />
          </div>
        )}

        <div>
          <label className="mb-1 block text-sm font-medium">Reason</label>
          <Select value={reason} onValueChange={setReason} disabled={windowExpired}>
            <SelectTrigger><SelectValue placeholder="Select reason" /></SelectTrigger>
            <SelectContent>
              {Object.entries(REASON_LABELS).map(([value, label]) => (
                <SelectItem key={value} value={value}>{label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium">Description</label>
          <Textarea
            placeholder="Describe the issue in detail..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={4}
            disabled={windowExpired}
          />
        </div>

        {error && <p className="text-sm text-destructive">{error}</p>}

        <Button
          onClick={handleSubmit}
          disabled={saving || !transactionId || !reason || !description || windowExpired}
          className="w-full"
        >
          {saving ? "Filing..." : "Submit Dispute"}
        </Button>
      </div>
    </DialogContent>
  );

  // Controlled mode: no trigger button rendered (parent controls open state)
  if (isControlled) {
    return <Dialog open={open} onOpenChange={setOpen}>{content}</Dialog>;
  }

  // Uncontrolled mode: renders its own trigger button
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm"><Plus className="h-4 w-4 mr-1" /> File Dispute</Button>
      </DialogTrigger>
      {content}
    </Dialog>
  );
}
