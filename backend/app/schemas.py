from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_validator

DISPUTE_WINDOW_DAYS = 120

ALLOWED_DISPUTE_REASONS = {"unauthorized", "duplicate", "wrong_amount", "not_received", "other"}


# --- Customer ---

class CustomerOut(BaseModel):
    customer_name: str
    email: str
    account_ids: list[UUID]


# --- Account ---

class AccountOut(BaseModel):
    id: UUID
    account_number: str
    customer_name: str
    email: str
    account_type: str
    balance: float
    currency: str
    status: str
    opened_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AccountDetail(AccountOut):
    transaction_count: int = 0
    total_debits: float = 0.0
    total_credits: float = 0.0
    open_disputes: int = 0


# --- Transaction ---

class TransactionOut(BaseModel):
    id: UUID
    account_id: UUID
    amount: float
    merchant_name: str
    merchant_category: str
    transaction_type: str
    description: str | None
    status: str
    transacted_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionListResponse(BaseModel):
    items: list[TransactionOut]
    total: int
    page: int
    per_page: int


# --- Dispute ---

class DisputeOut(BaseModel):
    id: UUID
    transaction_id: UUID
    account_id: UUID
    reason: str
    description: str
    status: str
    resolution_note: str | None
    filed_at: datetime
    resolved_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DisputeCreate(BaseModel):
    transaction_id: UUID
    reason: str
    description: str

    @field_validator("reason")
    @classmethod
    def reason_must_be_valid(cls, v: str) -> str:
        if v not in ALLOWED_DISPUTE_REASONS:
            raise ValueError(f"Reason must be one of: {', '.join(sorted(ALLOWED_DISPUTE_REASONS))}")
        return v


class DisputeUpdate(BaseModel):
    status: str
    resolution_note: str | None = None


# --- Dashboard ---

class DashboardSummary(BaseModel):
    total_accounts: int
    total_balance: float
    transaction_count: int
    transaction_volume: float
    open_disputes: int
    recent_transactions: list[TransactionOut]
