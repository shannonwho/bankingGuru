import uuid
from datetime import datetime, timedelta, timezone

from app.models import Account, Transaction, Dispute


def _create_account(db) -> Account:
    acct = Account(
        id=uuid.uuid4(),
        account_number="1234-5678-01",
        customer_name="Test User",
        email="test@example.com",
        account_type="checking",
        balance=10000.00,
    )
    db.add(acct)
    db.flush()
    return acct


def _create_transaction(db, account_id, *, days_ago=10):
    txn = Transaction(
        id=uuid.uuid4(),
        account_id=account_id,
        amount=-50.00,
        merchant_name="Test Merchant",
        merchant_category="groceries",
        transaction_type="purchase",
        status="completed",
        transacted_at=datetime.now(timezone.utc) - timedelta(days=days_ago),
    )
    db.add(txn)
    db.flush()
    return txn


# --- Happy path ---

def test_submit_dispute_happy_path(client, db):
    acct = _create_account(db)
    txn = _create_transaction(db, acct.id)
    db.commit()

    r = client.post("/api/v1/disputes", json={
        "transaction_id": str(txn.id),
        "reason": "unauthorized",
        "description": "I did not make this purchase.",
    })
    assert r.status_code == 201
    data = r.json()
    assert data["status"] == "submitted"
    assert data["account_id"] == str(acct.id)
    assert data["reason"] == "unauthorized"


# --- 404 / 409 / 422 on create ---

def test_dispute_on_nonexistent_transaction(client, db):
    r = client.post("/api/v1/disputes", json={
        "transaction_id": str(uuid.uuid4()),
        "reason": "unauthorized",
        "description": "Does not exist.",
    })
    assert r.status_code == 404


def test_duplicate_dispute_rejected(client, db):
    acct = _create_account(db)
    txn = _create_transaction(db, acct.id)
    db.commit()

    client.post("/api/v1/disputes", json={
        "transaction_id": str(txn.id),
        "reason": "unauthorized",
        "description": "First dispute.",
    })
    r = client.post("/api/v1/disputes", json={
        "transaction_id": str(txn.id),
        "reason": "duplicate",
        "description": "Second dispute.",
    })
    assert r.status_code == 409


# --- 120-day window boundary ---

def test_dispute_window_at_119_days_accepted(client, db):
    acct = _create_account(db)
    txn = _create_transaction(db, acct.id, days_ago=119)
    db.commit()

    r = client.post("/api/v1/disputes", json={
        "transaction_id": str(txn.id),
        "reason": "unauthorized",
        "description": "Within window.",
    })
    assert r.status_code == 201


def test_dispute_window_at_121_days_rejected(client, db):
    acct = _create_account(db)
    txn = _create_transaction(db, acct.id, days_ago=121)
    db.commit()

    r = client.post("/api/v1/disputes", json={
        "transaction_id": str(txn.id),
        "reason": "unauthorized",
        "description": "Too old.",
    })
    assert r.status_code == 422
    assert "120 days" in r.json()["detail"]


# --- State machine transitions ---

def test_valid_transition_submitted_to_under_review(client, db):
    acct = _create_account(db)
    txn = _create_transaction(db, acct.id)
    db.commit()

    dispute = client.post("/api/v1/disputes", json={
        "transaction_id": str(txn.id),
        "reason": "unauthorized",
        "description": "Test.",
    }).json()

    r = client.patch(f"/api/v1/disputes/{dispute['id']}", json={"status": "under_review"})
    assert r.status_code == 200
    assert r.json()["status"] == "under_review"


def test_valid_transition_under_review_to_resolved(client, db):
    acct = _create_account(db)
    txn = _create_transaction(db, acct.id)
    db.commit()

    dispute = client.post("/api/v1/disputes", json={
        "transaction_id": str(txn.id),
        "reason": "unauthorized",
        "description": "Test.",
    }).json()

    client.patch(f"/api/v1/disputes/{dispute['id']}", json={"status": "under_review"})
    r = client.patch(f"/api/v1/disputes/{dispute['id']}", json={
        "status": "resolved",
        "resolution_note": "Refund issued.",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "resolved"
    assert data["resolution_note"] == "Refund issued."
    assert data["resolved_at"] is not None


def test_invalid_transition_submitted_to_resolved(client, db):
    acct = _create_account(db)
    txn = _create_transaction(db, acct.id)
    db.commit()

    dispute = client.post("/api/v1/disputes", json={
        "transaction_id": str(txn.id),
        "reason": "unauthorized",
        "description": "Test.",
    }).json()

    r = client.patch(f"/api/v1/disputes/{dispute['id']}", json={"status": "resolved"})
    assert r.status_code == 422


def test_terminal_state_resolved_cannot_transition(client, db):
    acct = _create_account(db)
    txn = _create_transaction(db, acct.id)
    db.commit()

    dispute = client.post("/api/v1/disputes", json={
        "transaction_id": str(txn.id),
        "reason": "unauthorized",
        "description": "Test.",
    }).json()

    client.patch(f"/api/v1/disputes/{dispute['id']}", json={"status": "under_review"})
    client.patch(f"/api/v1/disputes/{dispute['id']}", json={"status": "resolved"})

    r = client.patch(f"/api/v1/disputes/{dispute['id']}", json={"status": "submitted"})
    assert r.status_code == 422


# --- GET endpoints ---

def test_list_disputes_filtered_by_customer(client, db):
    acct = _create_account(db)
    txn = _create_transaction(db, acct.id)
    db.commit()

    client.post("/api/v1/disputes", json={
        "transaction_id": str(txn.id),
        "reason": "unauthorized",
        "description": "Test.",
    })

    r = client.get("/api/v1/disputes?customer_name=Test User")
    assert r.status_code == 200
    disputes = r.json()
    assert len(disputes) == 1
    assert disputes[0]["account_id"] == str(acct.id)


def test_get_single_dispute(client, db):
    acct = _create_account(db)
    txn = _create_transaction(db, acct.id)
    db.commit()

    created = client.post("/api/v1/disputes", json={
        "transaction_id": str(txn.id),
        "reason": "not_received",
        "description": "Never arrived.",
    }).json()

    r = client.get(f"/api/v1/disputes/{created['id']}")
    assert r.status_code == 200
    assert r.json()["reason"] == "not_received"


def test_get_nonexistent_dispute(client):
    r = client.get(f"/api/v1/disputes/{uuid.uuid4()}")
    assert r.status_code == 404
