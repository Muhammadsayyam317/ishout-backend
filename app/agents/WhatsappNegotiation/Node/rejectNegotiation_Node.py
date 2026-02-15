def reject_negotiation_node(state):
    state["negotiation_status"] = "rejected"
    state["final_reply"] = (
        "Thanks for your time. We'll keep you in mind for future collaborations."
    )
    return state
