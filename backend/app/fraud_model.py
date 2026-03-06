HIGH_RISK_CATEGORIES = {"crypto_exchange", "wire_transfer", "gambling", "pawn_shop"}
UNUSUAL_HOURS = set(range(1, 5))  # 1am – 4am


def score_transaction(
    amount: float,
    merchant_category: str,
    hour_of_day: int,
    avg_customer_amount: float,
    is_account_frozen: bool = False,
) -> dict:
    """
    Score a single transaction for fraud probability.

    Returns:
        fraud_score    float [0.0 – 1.0]
        risk_level     "LOW" | "MEDIUM" | "HIGH"
        flags          list of plain-English reasons
    """
    score = 0.0
    flags = []

    # Rule 1: amount is 3x+ above this customer's average
    if avg_customer_amount > 0 and amount > avg_customer_amount * 3:
        score += 0.40
        flags.append(
            f"Amount ${amount:,.2f} is significantly above customer average "
            f"(${avg_customer_amount:,.2f})"
        )

    # Rule 2: high-risk merchant category
    if merchant_category.lower() in HIGH_RISK_CATEGORIES:
        score += 0.30
        flags.append(f"High-risk merchant category: {merchant_category}")

    # Rule 3: transaction at unusual hour
    if hour_of_day in UNUSUAL_HOURS:
        score += 0.20
        flags.append(f"Transaction occurred at unusual hour ({hour_of_day}:00)")

    # Rule 4: activity on a frozen account
    if is_account_frozen:
        score += 0.50
        flags.append("Transaction attempted on frozen account")

    fraud_score = min(round(score, 2), 1.0)

    if fraud_score >= 0.60:
        risk_level = "HIGH"
    elif fraud_score >= 0.30:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "fraud_score": fraud_score,
        "risk_level": risk_level,
        "flags": flags,
    }
