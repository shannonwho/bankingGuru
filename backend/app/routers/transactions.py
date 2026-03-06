from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Account, Transaction
from app.schemas import TransactionOut, TransactionListResponse

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
