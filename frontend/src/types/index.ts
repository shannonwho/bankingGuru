export interface Customer {
  customer_name: string;
  email: string;
  account_ids: string[];
}

export interface Account {
  id: string;
  account_number: string;
  customer_name: string;
  email: string;
  account_type: string;
  balance: number;
  currency: string;
  status: string;
  opened_at: string;
  created_at: string;
  updated_at: string;
}

export interface AccountDetail extends Account {
  transaction_count: number;
  total_debits: number;
  total_credits: number;
  open_disputes: number;
}

export interface Transaction {
  id: string;
  account_id: string;
  amount: number;
  merchant_name: string;
  merchant_category: string;
  transaction_type: string;
  description: string | null;
  status: string;
  transacted_at: string;
  created_at: string;
}

export interface TransactionListResponse {
  items: Transaction[];
  total: number;
  page: number;
  per_page: number;
}

export interface Dispute {
  id: string;
  transaction_id: string;
  account_id: string;
  reason: string;
  description: string;
  status: string;
  resolution_note: string | null;
  filed_at: string;
  resolved_at: string | null;
  created_at: string;
}

export interface DashboardSummary {
  total_accounts: number;
  total_balance: number;
  transaction_count: number;
  transaction_volume: number;
  open_disputes: number;
  recent_transactions: Transaction[];
}
