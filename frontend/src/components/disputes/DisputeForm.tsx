import { useState } from "react";
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
import { createDispute } from "@/lib/api";
import type { Dispute } from "@/types";
import { Plus } from "lucide-react";

const reasons = ["unauthorized", "duplicate", "wrong_amount", "not_received", "other"];

interface Props {
  onCreated: (d: Dispute) => void;
}

export function DisputeForm({ onCreated }: Props) {
  const [open, setOpen] = useState(false);
  const [transactionId, setTransactionId] = useState("");
  const [reason, setReason] = useState("");
  const [description, setDescription] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    if (!transactionId || !reason || !description) return;
    setSaving(true);
    setError("");
    try {
      const dispute = await createDispute({
        transaction_id: transactionId,
        reason,
        description,
      });
      onCreated(dispute);
      setOpen(false);
      setTransactionId("");
      setReason("");
      setDescription("");
    } catch (e: any) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm"><Plus className="h-4 w-4 mr-1" /> File Dispute</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>File a New Dispute</DialogTitle>
          <DialogDescription>Enter the transaction details and reason for the dispute.</DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium">Transaction ID</label>
            <Input
              placeholder="Paste transaction UUID"
              value={transactionId}
              onChange={(e) => setTransactionId(e.target.value)}
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Reason</label>
            <Select value={reason} onValueChange={setReason}>
              <SelectTrigger><SelectValue placeholder="Select reason" /></SelectTrigger>
              <SelectContent>
                {reasons.map((r) => (
                  <SelectItem key={r} value={r}>{r.replace("_", " ")}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Description</label>
            <Textarea
              placeholder="Describe the issue..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
            />
          </div>
          {error && <p className="text-sm text-destructive">{error}</p>}
          <Button onClick={handleSubmit} disabled={saving || !transactionId || !reason || !description} className="w-full">
            {saving ? "Filing..." : "Submit Dispute"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
