from app.seed import seed_data


def test_health(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_seed_and_list_accounts(client, db):
    r = client.post("/api/v1/seed")
    assert r.status_code == 200
    assert r.json()["accounts"] == 8

    r = client.get("/api/v1/accounts")
    assert r.status_code == 200
    assert len(r.json()) == 8


def test_customers_endpoint(client, db):
    client.post("/api/v1/seed")
    r = client.get("/api/v1/customers")
    assert r.status_code == 200
    customers = r.json()
    assert len(customers) == 5
    # Marcus Chen has 3 accounts (checking, savings, credit_card)
    marcus = next(c for c in customers if c["customer_name"] == "Marcus Chen")
    assert len(marcus["account_ids"]) == 3
    # Each customer has at least 1 account
    for c in customers:
        assert len(c["account_ids"]) >= 1


def test_accounts_filtered_by_customer(client, db):
    client.post("/api/v1/seed")
    r = client.get("/api/v1/accounts?customer_name=Aisha Patel")
    assert r.status_code == 200
    accounts = r.json()
    assert len(accounts) == 2  # checking + savings
    for a in accounts:
        assert a["customer_name"] == "Aisha Patel"


def test_transactions_filtered_by_customer(client, db):
    client.post("/api/v1/seed")
    # Get Yuki Tanaka's account (1 account)
    accounts = client.get("/api/v1/accounts?customer_name=Yuki Tanaka").json()
    assert len(accounts) == 1
    acct_id = accounts[0]["id"]

    r = client.get("/api/v1/transactions?customer_name=Yuki Tanaka&per_page=100")
    assert r.status_code == 200
    for item in r.json()["items"]:
        assert item["account_id"] == acct_id


def test_disputes_filtered_by_customer(client, db):
    client.post("/api/v1/seed")
    r = client.get("/api/v1/disputes?customer_name=Sofia Rodriguez")
    assert r.status_code == 200
    # All returned disputes should belong to Sofia's accounts
    sofia_accounts = client.get("/api/v1/accounts?customer_name=Sofia Rodriguez").json()
    sofia_ids = {a["id"] for a in sofia_accounts}
    for d in r.json():
        assert d["account_id"] in sofia_ids


def test_dashboard_summary_filtered(client, db):
    client.post("/api/v1/seed")
    r = client.get("/api/v1/dashboard/summary?customer_name=Marcus Chen")
    assert r.status_code == 200
    data = r.json()
    assert data["total_accounts"] == 3  # checking, savings, credit_card


def test_account_detail(client, db):
    client.post("/api/v1/seed")
    accounts = client.get("/api/v1/accounts").json()
    account_id = accounts[0]["id"]

    r = client.get(f"/api/v1/accounts/{account_id}")
    assert r.status_code == 200
    data = r.json()
    assert "transaction_count" in data
    assert "total_debits" in data
    assert "open_disputes" in data


def test_account_not_found(client):
    r = client.get("/api/v1/accounts/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_transactions_pagination(client, db):
    client.post("/api/v1/seed")
    r = client.get("/api/v1/transactions?page=1&per_page=5")
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 5
    assert data["per_page"] == 5
    assert data["total"] > 5


def test_transactions_filter_by_category(client, db):
    client.post("/api/v1/seed")
    r = client.get("/api/v1/transactions?category=groceries&per_page=100")
    assert r.status_code == 200
    for item in r.json()["items"]:
        assert item["merchant_category"] == "groceries"


def test_disputes_workflow(client, db):
    client.post("/api/v1/seed")

    # Get a completed transaction to dispute
    txns = client.get("/api/v1/transactions?status=completed&per_page=100").json()["items"]
    # Find one that doesn't already have a dispute
    disputes_resp = client.get("/api/v1/disputes").json()
    disputed_txn_ids = {d["transaction_id"] for d in disputes_resp}
    available_txn = next(
        (t for t in txns if t["id"] not in disputed_txn_ids and t["amount"] < 0),
        None,
    )
    assert available_txn is not None, "Need an undisputed transaction"

    # Create dispute
    r = client.post(
        "/api/v1/disputes",
        json={
            "transaction_id": available_txn["id"],
            "reason": "unauthorized",
            "description": "I did not make this purchase.",
        },
    )
    assert r.status_code == 201
    dispute = r.json()
    assert dispute["status"] == "open"
    dispute_id = dispute["id"]

    # Invalid transition: open -> resolved
    r = client.patch(f"/api/v1/disputes/{dispute_id}", json={"status": "resolved"})
    assert r.status_code == 422

    # Valid: open -> investigating
    r = client.patch(f"/api/v1/disputes/{dispute_id}", json={"status": "investigating"})
    assert r.status_code == 200
    assert r.json()["status"] == "investigating"

    # Valid: investigating -> resolved
    r = client.patch(
        f"/api/v1/disputes/{dispute_id}",
        json={"status": "resolved", "resolution_note": "Refund issued."},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "resolved"
    assert data["resolution_note"] == "Refund issued."
    assert data["resolved_at"] is not None

    # Terminal: resolved -> anything fails
    r = client.patch(f"/api/v1/disputes/{dispute_id}", json={"status": "open"})
    assert r.status_code == 422


def test_duplicate_dispute(client, db):
    client.post("/api/v1/seed")
    disputes = client.get("/api/v1/disputes").json()
    if disputes:
        txn_id = disputes[0]["transaction_id"]
        r = client.post(
            "/api/v1/disputes",
            json={"transaction_id": txn_id, "reason": "duplicate", "description": "Test"},
        )
        assert r.status_code == 409


def test_dashboard_summary(client, db):
    client.post("/api/v1/seed")
    r = client.get("/api/v1/dashboard/summary")
    assert r.status_code == 200
    data = r.json()
    assert data["total_accounts"] == 8
    assert data["transaction_count"] > 0
    assert len(data["recent_transactions"]) <= 10
