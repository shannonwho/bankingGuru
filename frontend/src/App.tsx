import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import { Shell } from "@/components/layout/Shell";
import { DashboardPage } from "@/pages/DashboardPage";
import { TransactionsPage } from "@/pages/TransactionsPage";
import { DisputesPage } from "@/pages/DisputesPage";
import { LoginPage } from "@/pages/LoginPage";

const AGENT_NAME = "Support Agent";

function AppRoutes() {
  const { customer } = useAuth();

  if (!customer) return <LoginPage />;

  const isAgent = customer.customer_name === AGENT_NAME;

  return (
    <Routes>
      <Route element={<Shell />}>
        <Route index element={<DashboardPage />} />
        <Route path="transactions" element={<TransactionsPage />} />
        <Route
          path="disputes"
          element={isAgent ? <DisputesPage /> : <Navigate to="/" replace />}
        />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
