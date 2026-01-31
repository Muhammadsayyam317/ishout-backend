from app.Schemas.instagram.negotiation_schema import InstagramConversationState


def check_missing_info(state: InstagramConversationState):
    print("Entering into Node Check Missing Info")
    print("--------------------------------")
    print(state)
    print("--------------------------------")
    print("Entering into Node Check Missing Info")
    if state.get("interest") is None:
        print("Interest is missing")
        return "ask_interest"
    if state.get("availability") is None:
        print("Availability is missing")
        return "ask_availability"
    if state.get("rate") is None:
        print("Rate is missing")
        return "ask_rate"
    print("Fetching pricing rules")
    return "fetch_pricing"
