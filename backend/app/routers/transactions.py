from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Account, Transaction
from app.schemas import TransactionOut, TransactionListResponse
from app.chaos import simulate_payment_api_call

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=TransactionListResponse)
def list_transactions(
    account_id: UUID | None = None,
    customer_name: str | None = None,
    category: str | None = None,
    transaction_type: str | None = None,
    status: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Transaction)

    if customer_name:
        acct_ids = [a.id for a in db.query(Account.id).filter(Account.customer_name == customer_name).all()]
        q = q.filter(Transaction.account_id.in_(acct_ids))
    if account_id:
        q = q.filter(Transaction.account_id == account_id)
    if category:
        q = q.filter(Transaction.merchant_category == category)
    if transaction_type:
        q = q.filter(Transaction.transaction_type == transaction_type)
    if status:
        q = q.filter(Transaction.status == status)
    if date_from:
        q = q.filter(Transaction.transacted_at >= date_from)
    if date_to:
        q = q.filter(Transaction.transacted_at <= date_to)

    total = q.count()
    items = (
        q.order_by(Transaction.transacted_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return TransactionListResponse(
        items=[TransactionOut.model_validate(t) for t in items],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(transaction_id: UUID, db: Session = Depends(get_db)):
    txn = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn


@router.post("/{transaction_id}/verify")
def verify_transaction(transaction_id: UUID, db: Session = Depends(get_db)):
    """Verify a transaction with the external payment processor. Demonstrates third-party API dependency."""
    txn = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    try:
        result = simulate_payment_api_call(str(txn.id), float(txn.amount))
        return {"transaction_id": str(txn.id), "verification": result}
    except ConnectionError as e:
        raise HTTPException(status_code=502, detail=str(e))
