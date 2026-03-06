import type {
  Account,
  AccountDetail,
  Customer,
  TransactionListResponse,
  Transaction,
  Dispute,
  DashboardSummary,
  FraudSummary,
} from "@/types";

const BASE = "/api/v1";

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

// Customers
export const getCustomers = () => fetchJSON<Customer[]>(`${BASE}/customers`);

// Accounts
export const getAccounts = (params: Record<string, string> = {}) => {
  const qs = new URLSearchParams(params);
  return fetchJSON<Account[]>(`${BASE}/accounts?${qs.toString()}`);
};

export const getAccount = (id: string) =>
  fetchJSON<AccountDetail>(`${BASE}/accounts/${id}`);

// Transactions
export function getTransactions(params: Record<string, string | number> = {}) {
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== "" && v !== undefined && v !== null) qs.set(k, String(v));
  }
  return fetchJSON<TransactionListResponse>(
    `${BASE}/transactions?${qs.toString()}`
  );
}

export const getTransaction = (id: string) =>
  fetchJSON<Transaction>(`${BASE}/transactions/${id}`);

// Disputes
export function getDisputes(params: Record<string, string> = {}) {
  const qs = new URLSearchParams(params);
  return fetchJSON<Dispute[]>(`${BASE}/disputes?${qs.toString()}`);
}

export const getDispute = (id: string) =>
  fetchJSON<Dispute>(`${BASE}/disputes/${id}`);

export const createDispute = (body: {
  transaction_id: string;
  reason: string;
  description: string;
}) =>
  fetchJSON<Dispute>(`${BASE}/disputes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

export const updateDispute = (
  id: string,
  body: { status: string; resolution_note?: string }
) =>
  fetchJSON<Dispute>(`${BASE}/disputes/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

// Dashboard
export const getDashboardSummary = (params: Record<string, string> = {}) => {
  const qs = new URLSearchParams(params);
  return fetchJSON<DashboardSummary>(`${BASE}/dashboard/summary?${qs.toString()}`);
};

// Fraud
export function getFraudScores(params: { customer_name?: string }) {
  const qs = new URLSearchParams();
  if (params.customer_name) qs.set("customer_name", params.customer_name);
  return fetchJSON<FraudSummary>(`${BASE}/fraud/scores?${qs}`);
}

// Seed
export const seedData = () =>
  fetchJSON<{ message: string }>(`${BASE}/seed`, { method: "POST" });
