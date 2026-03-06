from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.fraud_model import score_transaction
from app.models import Account, Transaction
from app.schemas import FraudSummary, ScoredTransaction

router = APIRouter(prefix="/fraud", tags=["fraud"])


@router.get("/scores", response_model=FraudSummary)
def get_fraud_scores(customer_name: str | None = None, db: Session = Depends(get_db)):
    acct_q = db.query(Account)
    if customer_name:
        acct_q = acct_q.filter(Account.customer_name == customer_name)
    accounts = acct_q.all()
    acct_ids = [a.id for a in accounts]
    acct_map = {a.id: a for a in accounts}

    if not acct_ids:
        return FraudSummary(
            total_scored=0,
            high_risk_count=0,
            medium_risk_count=0,
            low_risk_count=0,
            avg_fraud_score=0.0,
            scored_transactions=[],
        )

    # Precompute avg abs(amount) per account
    avg_rows = (
        db.query(Transaction.account_id, func.avg(func.abs(Transaction.amount)))
        .filter(Transaction.account_id.in_(acct_ids))
        .group_by(Transaction.account_id)
        .all()
    )
    avg_by_account: dict = {row[0]: float(row[1]) for row in avg_rows}

    transactions = (
        db.query(Transaction)
        .filter(Transaction.account_id.in_(acct_ids))
        .order_by(Transaction.transacted_at.desc())
        .limit(200)
        .all()
    )

    scored: list[ScoredTransaction] = []
    for txn in transactions:
        account = acct_map.get(txn.account_id)
        result = score_transaction(
            amount=abs(txn.amount),
            merchant_category=txn.merchant_category,
            hour_of_day=txn.transacted_at.hour,
            avg_customer_amount=avg_by_account.get(txn.account_id, 0.0),
            is_account_frozen=(account.status == "frozen") if account else False,
        )
        scored.append(ScoredTransaction(
            transaction_id=txn.id,
            account_id=txn.account_id,
            merchant_name=txn.merchant_name,
            merchant_category=txn.merchant_category,
            amount=txn.amount,
            transacted_at=txn.transacted_at,
            fraud_score=result["fraud_score"],
            risk_level=result["risk_level"],
            flags=result["flags"],
        ))

    high = sum(1 for s in scored if s.risk_level == "HIGH")
    medium = sum(1 for s in scored if s.risk_level == "MEDIUM")
    low = sum(1 for s in scored if s.risk_level == "LOW")
    avg_score = round(sum(s.fraud_score for s in scored) / len(scored), 3) if scored else 0.0

    return FraudSummary(
        total_scored=len(scored),
        high_risk_count=high,
        medium_risk_count=medium,
        low_risk_count=low,
        avg_fraud_score=avg_score,
        scored_transactions=scored,
    )
