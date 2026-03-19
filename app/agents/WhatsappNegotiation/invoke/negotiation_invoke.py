async def Negotiation_invoke(agent, state: dict, config: dict | None = None):
    try:
        final_state = await agent.ainvoke(state, config=config)
    except Exception as e:
        print(f"[Negotiation_invoke] Agent invocation failed: {e}")
        final_state = state
    return final_state
