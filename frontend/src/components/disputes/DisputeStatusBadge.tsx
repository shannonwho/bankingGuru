import { Badge } from "@/components/ui/badge";

const statusVariant: Record<string, "default" | "warning" | "success" | "destructive"> = {
  submitted: "warning",
  under_review: "default",
  resolved: "success",
  rejected: "destructive",
};

const statusLabel: Record<string, string> = {
  submitted: "Submitted",
  under_review: "Under Review",
  resolved: "Resolved",
  rejected: "Rejected",
};

export function DisputeStatusBadge({ status }: { status: string }) {
  return (
    <Badge variant={statusVariant[status] ?? "secondary"}>
      {statusLabel[status] ?? status}
    </Badge>
  );
}
