import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getCustomers } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import type { Customer } from "@/types";
import { User } from "lucide-react";

export function LoginPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [error, setError] = useState("");
  const { login } = useAuth();

  useEffect(() => {
    getCustomers()
      .then(setCustomers)
      .catch((e) => setError(e.message));
  }, []);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <div className="w-full max-w-3xl space-y-6">
        <div className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary">
            <span className="text-lg font-bold text-primary-foreground">FC</span>
          </div>
          <h1 className="text-2xl font-bold">FinTechCo</h1>
          <p className="mt-1 text-sm text-muted-foreground">Select your account to continue</p>
        </div>

        {error && <p className="text-center text-destructive">{error}</p>}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {customers.map((c) => (
            <Card
              key={c.email}
              className="cursor-pointer transition-colors hover:bg-accent"
              onClick={() => login(c)}
            >
              <CardHeader className="flex flex-row items-center gap-3 pb-2">
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10">
                  <User className="h-4 w-4 text-primary" />
                </div>
                <div className="min-w-0">
                  <CardTitle className="text-sm font-semibold truncate">{c.customer_name}</CardTitle>
                  <p className="text-xs text-muted-foreground truncate">{c.email}</p>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground">
                  {c.account_ids.length} account{c.account_ids.length !== 1 && "s"}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
