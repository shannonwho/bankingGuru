"""
Unit and integration tests for the dispute submission flow (DIS-10).

Covers:
- Happy path: filing a dispute creates a case with status=open
- 120-day dispute window enforcement
- Invalid reason code rejection
- Duplicate dispute prevention
- Valid status state machine transitions
- Terminal state enforcement
"""

from datetime import datetime, timedelta, timezone


from app.models import Account, Transaction
from app.schemas import DISPUTE_WINDOW_DAYS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_account(db) -> Account:
    acct = Account(
        account_number="TEST000001",
        customer_name="Test User",
        email="test@example.com",
        account_type="checking",
        balance=5000.00,
        currency="USD",
    )
    db.add(acct)
    db.commit()
    db.refresh(acct)
    return acct


def _make_transaction(db, account_id, *, days_ago: int = 10) -> Transaction:
    txn = Transaction(
        account_id=account_id,
        amount=-42.00,
        merchant_name="Test Merchant",
        merchant_category="retail",
        transaction_type="purchase",
        status="completed",
        transacted_at=datetime.now(timezone.utc) - timedelta(days=days_ago),
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


# ---------------------------------------------------------------------------
# Filing a dispute
# ---------------------------------------------------------------------------

def test_create_dispute_happy_path(client, db):
    acct = _make_account(db)
    txn = _make_transaction(db, acct.id, days_ago=5)

    r = client.post("/api/v1/disputes", json={
        "transaction_id": str(txn.id),
        "reason": "unauthorized",
        "description": "I did not make this purchase.",
    })

    assert r.status_code == 201
    data = r.json()
    assert data["status"] == "open"
    assert data["transaction_id"] == str(txn.id)
    assert data["account_id"] == str(acct.id)
    assert data["reason"] == "unauthorized"
    assert data["resolved_at"] is None


def test_create_dispute_all_valid_reason_codes(client, db):
    acct = _make_account(db)
    valid_reasons = ["unauthorized", "duplicate", "wrong_amount", "not_received", "other"]

    for i, reason in enumerate(valid_reasons):
        _make_transaction(db, acct.id, days_ago=5)
        # patch account_number to be unique per iteration
        acct2 = Account(
            account_number=f"TEST00000{i+2}",
            customer_name="Test User",
            email="test@example.com",
            account_type="checking",
            balance=1000.00,
            currency="USD",
        )
        db.add(acct2)
        db.commit()
        txn2 = _make_transaction(db, acct2.id, days_ago=5)

        r = client.post("/api/v1/disputes", json={
            "transaction_id": str(txn2.id),
            "reason": reason,
            "description": f"Testing reason code: {reason}",
        })
        assert r.status_code == 201, f"Expected 201 for reason={reason}, got {r.status_code}: {r.text}"


# ---------------------------------------------------------------------------
# 120-day dispute window
# ---------------------------------------------------------------------------

def test_dispute_window_exactly_at_boundary_accepted(client, db):
    acct = _make_account(db)
    # 119 days ago — just inside the window
    txn = _make_transaction(db, acct.id, days_ago=119)

    r = client.post("/api/v1/disputes", json={
        "transaction_id": str(txn.id),
        "reason": "wrong_amount",
        "description": "Charged wrong amount.",
    })
    assert r.status_code == 201


def test_dispute_window_expired_rejected(client, db):
    acct = _make_account(db)
    # 121 days ago — past the 120-day window
    txn = _make_transaction(db, acct.id, days_ago=121)

    r = client.post("/api/v1/disputes", json={
        "transaction_id": str(txn.id),
        "reason": "unauthorized",
        "description": "Old transaction dispute attempt.",
    })
    assert r.status_code == 422
    assert "Dispute window expired" in r.json()["detail"]
    assert str(DISPUTE_WINDOW_DAYS) in r.json()["detail"]


# ---------------------------------------------------------------------------
# Reason code validation
# ---------------------------------------------------------------------------

def test_invalid_reason_code_rejected(client, db):
    acct = _make_account(db)
    txn = _make_transaction(db, acct.id, days_ago=5)

    r = client.post("/api/v1/disputes", json={
        "transaction_id": str(txn.id),
        "reason": "not_a_real_reason",
        "description": "This should fail.",
    })
    assert r.status_code == 422


def test_empty_reason_rejected(client, db):
    acct = _make_account(db)
    txn = _make_transaction(db, acct.id, days_ago=5)

    r = client.post("/api/v1/disputes", json={
        "transaction_id": str(txn.id),
        "reason": "",
        "description": "Empty reason.",
    })
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Duplicate prevention
# ---------------------------------------------------------------------------

def test_duplicate_dispute_rejected(client, db):
    acct = _make_account(db)
    txn = _make_transaction(db, acct.id, days_ago=5)

    payload = {
        "transaction_id": str(txn.id),
        "reason": "unauthorized",
        "description": "First filing.",
    }
    r1 = client.post("/api/v1/disputes", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/api/v1/disputes", json={**payload, "description": "Second filing."})
    assert r2.status_code == 409
    assert "already exists" in r2.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Transaction not found
# ---------------------------------------------------------------------------

def test_dispute_nonexistent_transaction(client, db):
    r = client.post("/api/v1/disputes", json={
        "transaction_id": "00000000-0000-0000-0000-000000000000",
        "reason": "unauthorized",
        "description": "Ghost transaction.",
    })
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Status state machine
# ---------------------------------------------------------------------------

def test_status_transitions_open_to_investigating(client, db):
    acct = _make_account(db)
    txn = _make_transaction(db, acct.id)
    dispute = client.post("/api/v1/disputes", json={
        "transaction_id": str(txn.id),
        "reason": "not_received",
        "description": "Item never arrived.",
    }).json()

    r = client.patch(f"/api/v1/disputes/{dispute['id']}", json={"status": "investigating"})
    assert r.status_code == 200
    assert r.json()["status"] == "investigating"


def test_status_transitions_investigating_to_resolved_with_note(client, db):
    acct = _make_account(db)
    txn = _make_transaction(db, acct.id)
    dispute = client.post("/api/v1/disputes", json={
        "transaction_id": str(txn.id),
        "reason": "duplicate",
        "description": "Charged twice.",
    }).json()
    client.patch(f"/api/v1/disputes/{dispute['id']}", json={"status": "investigating"})

    r = client.patch(f"/api/v1/disputes/{dispute['id']}", json={
        "status": "resolved",
        "resolution_note": "Refund of $42.00 issued.",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "resolved"
    assert data["resolution_note"] == "Refund of $42.00 issued."
    assert data["resolved_at"] is not None


def test_invalid_transition_open_to_resolved_rejected(client, db):
    acct = _make_account(db)
    txn = _make_transaction(db, acct.id)
    dispute = client.post("/api/v1/disputes", json={
        "transaction_id": str(txn.id),
        "reason": "other",
        "description": "Testing invalid transition.",
    }).json()

    r = client.patch(f"/api/v1/disputes/{dispute['id']}", json={"status": "resolved"})
    assert r.status_code == 422


def test_terminal_state_blocks_further_transitions(client, db):
    acct = _make_account(db)
    txn = _make_transaction(db, acct.id)
    dispute = client.post("/api/v1/disputes", json={
        "transaction_id": str(txn.id),
        "reason": "unauthorized",
        "description": "Test terminal block.",
    }).json()
    client.patch(f"/api/v1/disputes/{dispute['id']}", json={"status": "denied"})

    r = client.patch(f"/api/v1/disputes/{dispute['id']}", json={"status": "investigating"})
    assert r.status_code == 422
    assert "terminal" in r.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------

def test_get_dispute_by_id(client, db):
    acct = _make_account(db)
    txn = _make_transaction(db, acct.id)
    created = client.post("/api/v1/disputes", json={
        "transaction_id": str(txn.id),
        "reason": "wrong_amount",
        "description": "Overcharged by $5.",
    }).json()

    r = client.get(f"/api/v1/disputes/{created['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == created["id"]


def test_get_dispute_not_found(client, db):
    r = client.get("/api/v1/disputes/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_list_disputes_filter_by_status(client, db):
    acct = _make_account(db)
    txn1 = _make_transaction(db, acct.id, days_ago=10)
    txn2 = _make_transaction(db, acct.id, days_ago=11)

    d1 = client.post("/api/v1/disputes", json={
        "transaction_id": str(txn1.id), "reason": "unauthorized", "description": "A",
    }).json()
    client.post("/api/v1/disputes", json={
        "transaction_id": str(txn2.id), "reason": "duplicate", "description": "B",
    })
    client.patch(f"/api/v1/disputes/{d1['id']}", json={"status": "investigating"})

    r = client.get("/api/v1/disputes?status=investigating")
    assert r.status_code == 200
    results = r.json()
    assert all(d["status"] == "investigating" for d in results)
