def close_conversation_node(state):
    state["negotiation_status"] = "closed"
    state["final_reply"] = "Thank you! Looking forward to working together."
    return state
