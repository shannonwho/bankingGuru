from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Account, Dispute, Transaction
from app.schemas import DisputeOut, DisputeCreate, DisputeUpdate, DISPUTE_WINDOW_DAYS

router = APIRouter(prefix="/disputes", tags=["disputes"])

VALID_TRANSITIONS = {
    "submitted": {"under_review", "rejected"},
    "under_review": {"resolved", "rejected"},
}


@router.get("", response_model=list[DisputeOut])
def list_disputes(
    status: str | None = None,
    account_id: UUID | None = None,
    customer_name: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Dispute)
    if customer_name:
        acct_ids = [a.id for a in db.query(Account.id).filter(Account.customer_name == customer_name).all()]
        q = q.filter(Dispute.account_id.in_(acct_ids))
    if status:
        q = q.filter(Dispute.status == status)
    if account_id:
        q = q.filter(Dispute.account_id == account_id)
    return q.order_by(Dispute.filed_at.desc()).all()


@router.get("/{dispute_id}", response_model=DisputeOut)
def get_dispute(dispute_id: UUID, db: Session = Depends(get_db)):
    dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")
    return dispute


@router.post("", response_model=DisputeOut, status_code=201)
def create_dispute(body: DisputeCreate, db: Session = Depends(get_db)):
    txn = db.query(Transaction).filter(Transaction.id == body.transaction_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    existing = db.query(Dispute).filter(Dispute.transaction_id == body.transaction_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Dispute already exists for this transaction")

    transacted_at = txn.transacted_at if txn.transacted_at.tzinfo else txn.transacted_at.replace(tzinfo=timezone.utc)
    age_days = (datetime.now(timezone.utc) - transacted_at).days
    if age_days > DISPUTE_WINDOW_DAYS:
        raise HTTPException(status_code=422, detail="Transaction is older than 120 days")

    dispute = Dispute(
        transaction_id=body.transaction_id,
        account_id=txn.account_id,
        reason=body.reason,
        description=body.description,
    )
    db.add(dispute)
    db.commit()
    db.refresh(dispute)
    return dispute


@router.patch("/{dispute_id}", response_model=DisputeOut)
def update_dispute(dispute_id: UUID, body: DisputeUpdate, db: Session = Depends(get_db)):
    dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")

    allowed = VALID_TRANSITIONS.get(dispute.status, set())
    if body.status not in allowed:
        raise HTTPException(
            status_code=422,
            detail=f"Cannot transition from '{dispute.status}' to '{body.status}'. Allowed: {sorted(allowed) if allowed else 'none (terminal state)'}",
        )

    dispute.status = body.status
    if body.resolution_note is not None:
        dispute.resolution_note = body.resolution_note
    if body.status in ("resolved", "rejected"):
        dispute.resolved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(dispute)
    return dispute
