# fraud_model.py
# ---------------------------------------------------------------
# Fraud scoring model — built by data science team
# Trained on 18 months of transaction history (offline, in Jupyter)
#
# Status: READY FOR PRODUCTION — needs backend integration
# Contact: ds-team@bankingguru.com
# ---------------------------------------------------------------

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


# ---------------------------------------------------------------
# Quick local test — run: python notebooks/fraud_model.py
# ---------------------------------------------------------------
if __name__ == "__main__":
    examples = [
        # Suspicious: large amount + bad category + odd hour
        dict(amount=4500, merchant_category="crypto_exchange", hour_of_day=2,
             avg_customer_amount=120, is_account_frozen=False),
        # Clean transaction
        dict(amount=85, merchant_category="groceries", hour_of_day=14,
             avg_customer_amount=95, is_account_frozen=False),
        # Borderline: slightly elevated amount, normal category
        dict(amount=380, merchant_category="electronics", hour_of_day=19,
             avg_customer_amount=110, is_account_frozen=False),
    ]

    for txn in examples:
        result = score_transaction(**txn)
        print(f"Amount: ${txn['amount']:>7,.2f} | "
              f"Category: {txn['merchant_category']:<18} | "
              f"Score: {result['fraud_score']:.2f} | "
              f"Risk: {result['risk_level']:<6} | "
              f"Flags: {len(result['flags'])}")
