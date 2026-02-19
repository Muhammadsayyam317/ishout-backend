from app.utils.printcolors import Colors


async def Negotiation_invoke(agent, state: dict, config: dict | None = None):
    print(
        f"{Colors.YELLOW}Entering Negotiation_invoke for thread {state.get('thread_id')}"
    )
    final_state = await agent.ainvoke(state, config=config)
    print(
        f"{Colors.GREEN}Exiting Negotiation_invoke for thread {state.get('thread_id')}"
    )
    return final_state
