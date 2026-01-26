from app.agents.Instagram.state.influencer_details_state import ConversationState


def check_missing_info(state: ConversationState):
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
