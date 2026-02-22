from agents import Agent, Runner
from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.Schemas.instagram.negotiation_schema import AnalyzeMessageOutput, NextAction
from app.Guardails.input_guardrails import WhatsappInputGuardrail
from app.utils.prompts import ANALYZE_INFLUENCER_WHATSAPP_PROMPT
from app.utils.printcolors import Colors


async def intentclassifier(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering intentclassifier node")
    print("--------------------------------")

    user_message = state.get("user_message", "")
    result = await Runner.run(
        Agent(
            name="analyze_whatsapp_message",
            instructions=ANALYZE_INFLUENCER_WHATSAPP_PROMPT,
            input_guardrails=[WhatsappInputGuardrail],
            output_type=AnalyzeMessageOutput,
        ),
        input=user_message,
    )

    analysis = result.final_output

    state["analysis"] = analysis
    state["intent"] = getattr(analysis, "intent", "unclear")
    state["next_action"] = getattr(
        analysis, "next_action", NextAction.GENERATE_CLARIFICATION
    )

    print(
        f"{Colors.CYAN}Intent → {state['intent']} | NextAction → {state['next_action']}"
    )
    print(f"{Colors.YELLOW}Exiting intentclassifier node")
    print("--------------------------------")

    return state
