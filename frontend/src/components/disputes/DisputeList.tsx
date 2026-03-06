import type { Dispute } from "@/types";
import { DisputeStatusBadge } from "@/components/disputes/DisputeStatusBadge";
import { formatDate } from "@/lib/utils";
import { cn } from "@/lib/utils";

interface Props {
  disputes: Dispute[];
  selectedId: string | null;
  onSelect: (d: Dispute) => void;
}

export function DisputeList({ disputes, selectedId, onSelect }: Props) {
  if (disputes.length === 0) {
    return <p className="p-4 text-sm text-muted-foreground">No disputes found.</p>;
  }

  return (
    <div className="divide-y">
      {disputes.map((d) => (
        <button
          key={d.id}
          onClick={() => onSelect(d)}
          className={cn(
            "flex w-full flex-col gap-1 px-4 py-3 text-left transition-colors hover:bg-muted/50",
            selectedId === d.id && "bg-muted"
          )}
        >
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium capitalize">{d.reason.replace("_", " ")}</span>
            <DisputeStatusBadge status={d.status} />
          </div>
          <span className="text-xs text-muted-foreground">
            Filed {formatDate(d.filed_at)}
          </span>
        </button>
      ))}
    </div>
  );
}
