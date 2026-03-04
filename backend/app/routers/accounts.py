from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Account, Transaction, Dispute
from app.schemas import AccountOut, AccountDetail

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=list[AccountOut])
def list_accounts(customer_name: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Account)
    if customer_name:
        q = q.filter(Account.customer_name == customer_name)
    return q.order_by(Account.customer_name).all()


@router.get("/{account_id}", response_model=AccountDetail)
def get_account(account_id: UUID, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    txn_stats = (
        db.query(
            func.count(Transaction.id).label("count"),
            func.coalesce(func.sum(case((Transaction.amount < 0, Transaction.amount), else_=0)), 0).label("debits"),
            func.coalesce(func.sum(case((Transaction.amount > 0, Transaction.amount), else_=0)), 0).label("credits"),
        )
        .filter(Transaction.account_id == account_id)
        .first()
    )

    open_disputes = (
        db.query(func.count(Dispute.id))
        .filter(Dispute.account_id == account_id, Dispute.status.in_(["open", "investigating"]))
        .scalar()
    )

    return AccountDetail(
        **AccountOut.model_validate(account).model_dump(),
        transaction_count=txn_stats.count,
        total_debits=float(txn_stats.debits),
        total_credits=float(txn_stats.credits),
        open_disputes=open_disputes,
    )
