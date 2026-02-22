from app.utils.printcolors import Colors


async def Negotiation_invoke(agent, state: dict, config: dict | None = None):
    print(
        f"{Colors.YELLOW}Entering Negotiation_invoke for thread {state.get('thread_id')}"
    )
    try:
        final_state = await agent.ainvoke(state, config=config)
    except Exception as e:
        print(f"[Negotiation_invoke] Agent invocation failed: {e}")
        final_state = state
    print(
        f"{Colors.GREEN}Exiting Negotiation_invoke for thread {state.get('thread_id')}"
    )
    return final_state
