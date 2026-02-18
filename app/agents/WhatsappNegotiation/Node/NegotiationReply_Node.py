from agents import Agent, Runner
from agents.exceptions import InputGuardrailTripwireTriggered
from app.Guardails.input_guardrails import WhatsappInputGuardrail
from app.Schemas.instagram.negotiation_schema import GenerateReplyOutput
from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.utils.message_context import build_whatsapp_message_context
from app.utils.prompts import NEGOTIATE_INFLUENCER_DM_PROMPT
from app.utils.printcolors import Colors


async def generate_reply_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering generate_reply_node")
    print("--------------------------------")

    try:
        prompt = NEGOTIATE_INFLUENCER_DM_PROMPT.format(
            min_price=state.get("min_price"),
            max_price=state.get("max_price"),
            last_offer=state.get("last_offered_price"),
            negotiation_status=state.get("negotiation_status"),
            next_action=state.get("next_action"),
        )

        result = await Runner.run(
            Agent(
                name="whatsapp_negotiation_reply",
                instructions=prompt,
                input_guardrails=[WhatsappInputGuardrail],
                output_type=GenerateReplyOutput,
            ),
            input=build_whatsapp_message_context(
                state.get("history", []),
                state.get("user_message"),
            ),
        )
        print(f"{Colors.CYAN}History: {state.get('history')}")
        print("--------------------------------")
        print(f"{Colors.CYAN}User Message: {state.get('user_message')}")
        print("--------------------------------")
        print(f"{Colors.CYAN}Result: {result}")

        reply_text = result.final_output["final_reply"]
        print(f"{Colors.CYAN}Reply Text: {reply_text}")
        print("--------------------------------")
        state["negotiation_mode"] = "automatic"

    except InputGuardrailTripwireTriggered as e:
        reply_text = (
            e.fallback or "Thanks for your message. Our team will follow up shortly."
        )
        state["negotiation_mode"] = "manual"
        state["manual_reason"] = e.reason

    state["final_reply"] = reply_text

    # Save AI reply into history
    state.setdefault("history", []).append({"sender_type": "AI", "message": reply_text})

    print(f"{Colors.CYAN}Generated Reply: {reply_text}")
    print(f"{Colors.YELLOW}Exiting generate_reply_node")
    print("--------------------------------")

    return state
