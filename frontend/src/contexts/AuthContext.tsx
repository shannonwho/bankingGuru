import { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import type { Customer } from "@/types";

interface AuthContextType {
  customer: Customer | null;
  login: (customer: Customer) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

const STORAGE_KEY = "fintechco_customer";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [customer, setCustomer] = useState<Customer | null>(() => {
    const stored = sessionStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : null;
  });

  const login = (c: Customer) => {
    setCustomer(c);
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(c));
  };

  const logout = () => {
    setCustomer(null);
    sessionStorage.removeItem(STORAGE_KEY);
  };

  return (
    <AuthContext.Provider value={{ customer, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
