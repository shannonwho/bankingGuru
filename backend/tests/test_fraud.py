"""
Tests for the fraud scoring model and API endpoint.

Covers:
- Fraud model: each scoring rule individually and combined
- Risk level thresholds (LOW < 0.30, MEDIUM < 0.60, HIGH >= 0.60)
- API endpoint: happy path, empty results, customer filtering
"""

from datetime import datetime, timedelta, timezone

from app.fraud_model import score_transaction, HIGH_RISK_CATEGORIES, UNUSUAL_HOURS
from app.models import Account, Transaction


# ---------------------------------------------------------------------------
# Unit tests — score_transaction function
# ---------------------------------------------------------------------------

def test_score_low_risk_normal_transaction():
    result = score_transaction(
        amount=50.0,
        merchant_category="groceries",
        hour_of_day=14,
        avg_customer_amount=60.0,
    )
    assert result["fraud_score"] == 0.0
    assert result["risk_level"] == "LOW"
    assert result["flags"] == []


def test_score_flags_amount_above_3x_average():
    result = score_transaction(
        amount=200.0,
        merchant_category="groceries",
        hour_of_day=14,
        avg_customer_amount=50.0,
    )
    assert result["fraud_score"] == 0.40
    assert "significantly above customer average" in result["flags"][0]


def test_score_no_amount_flag_when_avg_is_zero():
    result = score_transaction(
        amount=9999.0,
        merchant_category="groceries",
        hour_of_day=14,
        avg_customer_amount=0.0,
    )
    assert result["fraud_score"] == 0.0
    assert result["flags"] == []


def test_score_flags_high_risk_merchant_category():
    for category in HIGH_RISK_CATEGORIES:
        result = score_transaction(
            amount=50.0,
            merchant_category=category,
            hour_of_day=14,
            avg_customer_amount=50.0,
        )
        assert result["fraud_score"] == 0.30
        assert any("High-risk merchant category" in f for f in result["flags"])


def test_score_flags_unusual_hour():
    for hour in UNUSUAL_HOURS:
        result = score_transaction(
            amount=50.0,
            merchant_category="groceries",
            hour_of_day=hour,
            avg_customer_amount=50.0,
        )
        assert result["fraud_score"] == 0.20
        assert any("unusual hour" in f for f in result["flags"])


def test_score_normal_hours_not_flagged():
    for hour in [0, 5, 12, 18, 23]:
        result = score_transaction(
            amount=50.0,
            merchant_category="groceries",
            hour_of_day=hour,
            avg_customer_amount=50.0,
        )
        assert not any("unusual hour" in f for f in result["flags"])


def test_score_flags_frozen_account():
    result = score_transaction(
        amount=50.0,
        merchant_category="groceries",
        hour_of_day=14,
        avg_customer_amount=50.0,
        is_account_frozen=True,
    )
    assert result["fraud_score"] == 0.50
    assert any("frozen account" in f for f in result["flags"])


def test_score_capped_at_1_0():
    result = score_transaction(
        amount=999.0,
        merchant_category="crypto_exchange",
        hour_of_day=2,
        avg_customer_amount=10.0,
        is_account_frozen=True,
    )
    # 0.40 + 0.30 + 0.20 + 0.50 = 1.40 → capped at 1.0
    assert result["fraud_score"] == 1.0
    assert result["risk_level"] == "HIGH"
    assert len(result["flags"]) == 4


def test_risk_level_thresholds():
    # LOW: score < 0.30
    r = score_transaction(amount=50, merchant_category="groceries", hour_of_day=2, avg_customer_amount=50)
    assert r["fraud_score"] == 0.20
    assert r["risk_level"] == "LOW"

    # MEDIUM: 0.30 <= score < 0.60
    r = score_transaction(amount=50, merchant_category="crypto_exchange", hour_of_day=14, avg_customer_amount=50)
    assert r["fraud_score"] == 0.30
    assert r["risk_level"] == "MEDIUM"

    # HIGH: score >= 0.60
    r = score_transaction(amount=500, merchant_category="crypto_exchange", hour_of_day=2, avg_customer_amount=50)
    assert r["fraud_score"] == 0.90
    assert r["risk_level"] == "HIGH"


# ---------------------------------------------------------------------------
# Integration tests — /api/v1/fraud/scores endpoint
# ---------------------------------------------------------------------------

def _make_account(db, *, customer_name="Test User", account_number="FRAUD00001") -> Account:
    acct = Account(
        account_number=account_number,
        customer_name=customer_name,
        email="test@example.com",
        account_type="checking",
        balance=5000.00,
        currency="USD",
    )
    db.add(acct)
    db.commit()
    db.refresh(acct)
    return acct


def _make_transaction(db, account_id, *, amount=-50.0, category="groceries", hours_ago=5) -> Transaction:
    txn = Transaction(
        account_id=account_id,
        amount=amount,
        merchant_name="Test Merchant",
        merchant_category=category,
        transaction_type="purchase",
        status="completed",
        transacted_at=datetime.now(timezone.utc) - timedelta(hours=hours_ago),
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


def test_fraud_scores_endpoint_returns_scored_transactions(client, db):
    acct = _make_account(db)
    _make_transaction(db, acct.id)

    r = client.get("/api/v1/fraud/scores")
    assert r.status_code == 200
    data = r.json()
    assert data["total_scored"] == 1
    assert len(data["scored_transactions"]) == 1
    txn = data["scored_transactions"][0]
    assert "fraud_score" in txn
    assert "risk_level" in txn
    assert "flags" in txn


def test_fraud_scores_empty_when_no_accounts(client, db):
    r = client.get("/api/v1/fraud/scores")
    assert r.status_code == 200
    data = r.json()
    assert data["total_scored"] == 0
    assert data["scored_transactions"] == []


def test_fraud_scores_filtered_by_customer_name(client, db):
    acct1 = _make_account(db, customer_name="Alice", account_number="FRAUD00001")
    acct2 = _make_account(db, customer_name="Bob", account_number="FRAUD00002")
    _make_transaction(db, acct1.id)
    _make_transaction(db, acct2.id)

    r = client.get("/api/v1/fraud/scores?customer_name=Alice")
    assert r.status_code == 200
    data = r.json()
    assert data["total_scored"] == 1
    assert all(t["account_id"] == str(acct1.id) for t in data["scored_transactions"])


def test_fraud_scores_risk_counts_are_consistent(client, db):
    acct = _make_account(db)
    _make_transaction(db, acct.id, amount=-50.0, category="groceries")
    _make_transaction(db, acct.id, amount=-50.0, category="crypto_exchange")

    r = client.get("/api/v1/fraud/scores")
    assert r.status_code == 200
    data = r.json()
    assert data["high_risk_count"] + data["medium_risk_count"] + data["low_risk_count"] == data["total_scored"]


def test_fraud_scores_unknown_customer_returns_empty(client, db):
    _make_account(db)
    r = client.get("/api/v1/fraud/scores?customer_name=Nonexistent")
    assert r.status_code == 200
    assert r.json()["total_scored"] == 0
