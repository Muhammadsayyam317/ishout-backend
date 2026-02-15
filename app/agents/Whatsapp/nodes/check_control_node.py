from app.model.whatsappconversation import AgentControl
from app.db.connection import get_db
from app.utils.printcolors import Colors


async def node_check_agent_control(state):
    print(f"{Colors.GREEN}Entering into node_check_agent_control")
    print("--------------------------------")
    db = get_db()
    control: AgentControl = await db.get_collection("agent_controls").find_one(
        {"thread_id": state["sender_id"]}
    )

    print(f"{Colors.CYAN}Control: {control}")
    print("--------------------------------")
    # Human takeover
    if control:
        if control.get("human_takeover"):
            state["blocked"] = True
            state["block_reason"] = "HUMAN_TAKEOVER"
            state["reply"] = None
            state["reply_sent"] = True
            state["done"] = True
            return state

        # ⏸ Agent paused → send auto message
        if control.get("agent_paused"):
            state["blocked"] = True
            state["block_reason"] = "AGENT_PAUSED"
            state["reply"] = (
                "⏸️ Our agent is currently paused.\n" "A human will respond you shortly."
            )
            state["reply_sent"] = False
            state["done"] = False
            print(f"{Colors.YELLOW}Exiting from node_check_agent_control")
            print("--------------------------------")
            return state

    state["blocked"] = False
    print(f"{Colors.YELLOW}Exiting from node_check_agent_control")
    print("--------------------------------")
    print(f"{Colors.CYAN}State: {state}")
    print("--------------------------------")
    return state
