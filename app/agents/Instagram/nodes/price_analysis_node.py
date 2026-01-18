def decide_next_step(analysis, min_price, max_price):
    if analysis.pricing_mentioned and analysis.budget_amount is not None:
        price = analysis.budget_amount

        if price > max_price:
            return "COUNTER_DOWN"

        if price < min_price:
            return "ACCEPT_BELOW_MIN"

        return "ALIGN_RANGE"

    return analysis.recommended_next_action
