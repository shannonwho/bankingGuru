import type { Account } from "@/types";
import { AccountCard } from "./AccountCard";

export function AccountList({ accounts }: { accounts: Account[] }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {accounts.map((a) => (
        <AccountCard key={a.id} account={a} />
      ))}
    </div>
  );
}
