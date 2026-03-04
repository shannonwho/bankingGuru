import random
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import Account, Transaction, Dispute

CUSTOMER_NAMES = [
    "Aisha Patel", "Marcus Chen", "Sofia Rodriguez", "James O'Brien", "Yuki Tanaka",
    "Priya Sharma", "David Kim", "Elena Volkov", "Omar Hassan", "Maria Santos",
    "Wei Zhang", "Fatima Al-Rashid", "Carlos Mendoza", "Hannah Johansson", "Kofi Asante",
]

MERCHANTS = {
    "groceries": [
        ("Whole Foods Market", (15, 250)),
        ("Trader Joe's", (12, 180)),
        ("Costco Wholesale", (50, 400)),
        ("Safeway", (20, 200)),
    ],
    "dining": [
        ("Starbucks", (4.50, 12)),
        ("Chipotle Mexican Grill", (9, 18)),
        ("The Cheesecake Factory", (25, 85)),
        ("DoorDash", (15, 65)),
    ],
    "travel": [
        ("United Airlines", (150, 1200)),
        ("Marriott Hotels", (120, 450)),
        ("Uber", (8, 55)),
        ("Lyft", (7, 45)),
    ],
    "utilities": [
        ("Pacific Gas & Electric", (80, 250)),
        ("AT&T Wireless", (45, 120)),
        ("Comcast Xfinity", (60, 150)),
        ("City Water Department", (30, 90)),
    ],
    "entertainment": [
        ("Netflix", (15.49, 22.99)),
        ("Spotify", (10.99, 16.99)),
        ("AMC Theatres", (12, 35)),
        ("Steam Games", (5, 70)),
    ],
    "transfer": [
        ("Venmo Transfer", (10, 500)),
        ("Zelle Payment", (20, 1000)),
        ("Wire Transfer", (100, 5000)),
    ],
}

# 5 customers, some with multiple accounts (8 accounts total)
CUSTOMER_ACCOUNTS = [
    ("Aisha Patel", "aisha.patel@email.com", ["checking", "savings"]),
    ("Marcus Chen", "marcus.chen@email.com", ["checking", "savings", "credit_card"]),
    ("Sofia Rodriguez", "sofia.rodriguez@email.com", ["checking"]),
    ("James O'Brien", "james.obrien@email.com", ["credit_card"]),
    ("Yuki Tanaka", "yuki.tanaka@email.com", ["checking"]),
]

DISPUTE_REASONS = ["unauthorized", "duplicate", "wrong_amount", "not_received", "other"]
DISPUTE_STATUSES = ["open", "open", "investigating", "investigating", "resolved", "denied"]


def seed_data(db: Session) -> dict:
    # Truncate in order
    db.query(Dispute).delete()
    db.query(Transaction).delete()
    db.query(Account).delete()
    db.commit()

    now = datetime.now(timezone.utc)
    accounts = []
    all_transactions = []

    # Create accounts — 5 customers, some with multiple accounts (8 total)
    acct_index = 0
    for name, email, acct_types in CUSTOMER_ACCOUNTS:
        for acct_type in acct_types:
            acct = Account(
                id=uuid.uuid4(),
                account_number=f"{random.randint(1000,9999)}-{random.randint(1000,9999)}-{random.randint(10,99):02d}",
                customer_name=name,
                email=email,
                account_type=acct_type,
                balance=round(random.uniform(500, 50000), 2),
                currency="USD",
                status="active" if acct_index < 7 else "frozen",
                opened_at=now - timedelta(days=random.randint(90, 730)),
            )
            accounts.append(acct)
            db.add(acct)
            acct_index += 1

    db.flush()

    # Create transactions for each account
    for acct in accounts:
        num_txns = random.randint(30, 80)
        for _ in range(num_txns):
            category = random.choice(list(MERCHANTS.keys()))
            merchant_name, (min_amt, max_amt) = random.choice(MERCHANTS[category])
            amount = round(random.uniform(min_amt, max_amt), 2)

            if category == "transfer":
                txn_type = "transfer"
                # Transfers can be positive or negative
                if random.random() < 0.4:
                    amount = amount  # incoming
                else:
                    amount = -amount
            elif merchant_name in ("Venmo Transfer", "Zelle Payment"):
                txn_type = "transfer"
            else:
                txn_type = "purchase"
                amount = -amount  # purchases are debits

            # Some deposits/credits
            if random.random() < 0.05:
                txn_type = "deposit"
                amount = round(random.uniform(500, 5000), 2)
            elif random.random() < 0.03:
                txn_type = "refund"
                amount = round(random.uniform(10, 200), 2)

            status = random.choices(
                ["completed", "pending", "failed"],
                weights=[0.85, 0.10, 0.05],
            )[0]

            txn = Transaction(
                id=uuid.uuid4(),
                account_id=acct.id,
                amount=amount,
                merchant_name=merchant_name,
                merchant_category=category,
                transaction_type=txn_type,
                description=None,
                status=status,
                transacted_at=now - timedelta(
                    days=random.randint(0, 90),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59),
                ),
            )
            all_transactions.append(txn)
            db.add(txn)

    db.flush()

    # Create 5-8 disputes on random completed purchase transactions
    eligible_txns = [t for t in all_transactions if t.status == "completed" and t.amount < 0]
    dispute_txns = random.sample(eligible_txns, min(random.randint(5, 8), len(eligible_txns)))

    disputes_created = 0
    for txn in dispute_txns:
        status = random.choice(DISPUTE_STATUSES)
        dispute = Dispute(
            id=uuid.uuid4(),
            transaction_id=txn.id,
            account_id=txn.account_id,
            reason=random.choice(DISPUTE_REASONS),
            description=f"Customer disputes charge of ${abs(txn.amount):.2f} at {txn.merchant_name}.",
            status=status,
            resolution_note="Reviewed and processed." if status in ("resolved", "denied") else None,
            filed_at=txn.transacted_at + timedelta(days=random.randint(1, 7)),
            resolved_at=(txn.transacted_at + timedelta(days=random.randint(8, 21))) if status in ("resolved", "denied") else None,
        )
        db.add(dispute)
        disputes_created += 1

    db.commit()

    return {
        "accounts": len(accounts),
        "transactions": len(all_transactions),
        "disputes": disputes_created,
    }
