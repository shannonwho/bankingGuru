import { NavLink } from "react-router-dom";
import { LayoutDashboard, ArrowLeftRight, ShieldAlert, LogOut } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";

const links = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/transactions", label: "Transactions", icon: ArrowLeftRight },
  { to: "/disputes", label: "Disputes", icon: ShieldAlert },
];

export function Sidebar() {
  const { customer, logout } = useAuth();

  return (
    <aside className="flex h-screen w-60 flex-col border-r bg-sidebar-background">
      <div className="flex h-14 items-center gap-2 border-b px-4">
        <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
          <span className="text-sm font-bold text-primary-foreground">BG</span>
        </div>
        <span className="text-lg font-semibold">Banking Guru</span>
      </div>
      <nav className="flex-1 space-y-1 p-3">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-sidebar-accent text-sidebar-accent-foreground"
                  : "text-sidebar-foreground hover:bg-sidebar-accent/50"
              )
            }
          >
            <Icon className="h-4 w-4" />
            {label}
          </NavLink>
        ))}
      </nav>
      {customer && (
        <div className="border-t p-3">
          <div className="mb-2 px-1">
            <p className="text-sm font-medium truncate">{customer.customer_name}</p>
            <p className="text-xs text-muted-foreground truncate">{customer.email}</p>
          </div>
          <Button variant="ghost" size="sm" className="w-full justify-start gap-2" onClick={logout}>
            <LogOut className="h-4 w-4" />
            Switch Account
          </Button>
        </div>
      )}
    </aside>
  );
}
