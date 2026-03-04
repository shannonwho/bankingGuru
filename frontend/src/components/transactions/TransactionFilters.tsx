import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export interface Filters {
  category: string;
  transaction_type: string;
  status: string;
  date_from: string;
  date_to: string;
}

interface Props {
  filters: Filters;
  onChange: (f: Filters) => void;
  onReset: () => void;
}

const categories = ["", "groceries", "dining", "travel", "utilities", "entertainment", "transfer"];
const types = ["", "purchase", "payment", "transfer", "deposit", "withdrawal", "refund"];
const statuses = ["", "completed", "pending", "failed"];

export function TransactionFilters({ filters, onChange, onReset }: Props) {
  const set = (key: keyof Filters, value: string) =>
    onChange({ ...filters, [key]: value });

  return (
    <div className="flex flex-wrap items-end gap-3">
      <div className="w-40">
        <label className="mb-1 block text-xs text-muted-foreground">Category</label>
        <Select value={filters.category} onValueChange={(v) => set("category", v)}>
          <SelectTrigger><SelectValue placeholder="All" /></SelectTrigger>
          <SelectContent>
            {categories.map((c) => (
              <SelectItem key={c || "all"} value={c || "all"}>{c || "All"}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="w-40">
        <label className="mb-1 block text-xs text-muted-foreground">Type</label>
        <Select value={filters.transaction_type} onValueChange={(v) => set("transaction_type", v)}>
          <SelectTrigger><SelectValue placeholder="All" /></SelectTrigger>
          <SelectContent>
            {types.map((t) => (
              <SelectItem key={t || "all"} value={t || "all"}>{t || "All"}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="w-36">
        <label className="mb-1 block text-xs text-muted-foreground">Status</label>
        <Select value={filters.status} onValueChange={(v) => set("status", v)}>
          <SelectTrigger><SelectValue placeholder="All" /></SelectTrigger>
          <SelectContent>
            {statuses.map((s) => (
              <SelectItem key={s || "all"} value={s || "all"}>{s || "All"}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="w-40">
        <label className="mb-1 block text-xs text-muted-foreground">From</label>
        <Input type="date" value={filters.date_from} onChange={(e) => set("date_from", e.target.value)} />
      </div>

      <div className="w-40">
        <label className="mb-1 block text-xs text-muted-foreground">To</label>
        <Input type="date" value={filters.date_to} onChange={(e) => set("date_to", e.target.value)} />
      </div>

      <Button variant="outline" size="sm" onClick={onReset}>Reset</Button>
    </div>
  );
}
