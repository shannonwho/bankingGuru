from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import engine, get_db, Base
from app.models import Account, Transaction, Dispute
from app.schemas import CustomerOut, DashboardSummary, TransactionOut
from app.seed import seed_data
from app.routers import accounts, transactions, disputes

app = FastAPI(title="FinTechCo API", version="0.1.0")

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accounts.router, prefix="/api/v1")
app.include_router(transactions.router, prefix="/api/v1")
app.include_router(disputes.router, prefix="/api/v1")


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/seed")
def run_seed(db: Session = Depends(get_db)):
    result = seed_data(db)
    return {"message": "Data seeded successfully", **result}


@app.get("/api/v1/customers", response_model=list[CustomerOut])
def list_customers(db: Session = Depends(get_db)):
    rows = (
        db.query(Account.customer_name, Account.email, Account.id)
        .order_by(Account.customer_name)
        .all()
    )
    from collections import defaultdict
    grouped: dict[tuple[str, str], list] = defaultdict(list)
    for name, email, acct_id in rows:
        grouped[(name, email)].append(acct_id)
    return [
        CustomerOut(customer_name=name, email=email, account_ids=ids)
        for (name, email), ids in grouped.items()
    ]


@app.get("/api/v1/dashboard/summary", response_model=DashboardSummary)
def dashboard_summary(customer_name: str | None = None, db: Session = Depends(get_db)):
    acct_q = db.query(Account)
    if customer_name:
        acct_q = acct_q.filter(Account.customer_name == customer_name)
    acct_ids = [a.id for a in acct_q.all()]

    total_accounts = len(acct_ids)
    total_balance = float(
        db.query(func.coalesce(func.sum(Account.balance), 0))
        .filter(Account.id.in_(acct_ids) if acct_ids else Account.id.is_(None))
        .scalar()
    ) if acct_ids else 0.0

    txn_q = db.query(Transaction)
    if customer_name:
        txn_q = txn_q.filter(Transaction.account_id.in_(acct_ids) if acct_ids else Transaction.account_id.is_(None))

    txn_count = txn_q.count()
    txn_volume = float(
        txn_q.with_entities(func.coalesce(func.sum(func.abs(Transaction.amount)), 0)).scalar()
    )

    disp_q = db.query(func.count(Dispute.id)).filter(Dispute.status.in_(["open", "investigating"]))
    if customer_name:
        disp_q = disp_q.filter(Dispute.account_id.in_(acct_ids) if acct_ids else Dispute.account_id.is_(None))
    open_disputes = disp_q.scalar()

    recent_q = db.query(Transaction)
    if customer_name:
        recent_q = recent_q.filter(Transaction.account_id.in_(acct_ids) if acct_ids else Transaction.account_id.is_(None))
    recent = recent_q.order_by(Transaction.transacted_at.desc()).limit(10).all()

    return DashboardSummary(
        total_accounts=total_accounts,
        total_balance=total_balance,
        transaction_count=txn_count,
        transaction_volume=txn_volume,
        open_disputes=open_disputes,
        recent_transactions=[TransactionOut.model_validate(t) for t in recent],
    )
