def calculate_rule_score(transaction):
    """
    Calculate fraud risk using deterministic business rules.

    Returns:
        rule_score: numeric risk score
        reasons: list of human-readable explanations
    """

    rule_score = 0
    reasons = []

    # Rule 1: High transaction amount
    if transaction.amount > 10000:
        rule_score += 25
        reasons.append(
            "Transaction amount is unusually high"
        )

    # Rule 2: New device
    if transaction.is_new_device == 1:
        rule_score += 20
        reasons.append(
            "Transaction was made from a new device"
        )

    # Rule 3: Large distance from previous transaction
    if transaction.distance_from_previous > 500:
        rule_score += 25
        reasons.append(
            "Transaction location is unusually far from previous activity"
        )

    # Rule 4: Night transaction
    if transaction.is_night == 1:
        rule_score += 10
        reasons.append(
            "Transaction occurred during unusual hours"
        )

    # Rule 5: Very low transaction history
    if transaction.previous_transactions < 2:
        rule_score += 10
        reasons.append(
            "User has very little previous transaction history"
        )

    # Keep score between 0 and 100
    rule_score = min(rule_score, 100)

    return rule_score, reasons