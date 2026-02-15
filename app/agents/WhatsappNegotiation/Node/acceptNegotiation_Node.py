def accept_negotiation_node(state):
    state["negotiation_status"] = "agreed"
    state["final_reply"] = (
        "Great! We’re happy to proceed at this rate. We'll share next steps shortly."
    )
    return state
