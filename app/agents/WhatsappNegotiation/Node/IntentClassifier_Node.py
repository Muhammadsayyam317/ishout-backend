from app.Schemas.instagram.negotiation_schema import (
    AnalyzeMessageOutput,
    NextAction,
)
from app.Schemas.whatsapp.negotiation_schema import (
    WhatsappMessageIntent,
    WhatsappNegotiationState,
)
from agents import Agent, Runner
from app.utils.printcolors import Colors
from app.utils.prompts import ANALYZE_INFLUENCER_WHATSAPP_PROMPT


async def intentclassifier(state: WhatsappNegotiationState):
    try:
        print(f"{Colors.GREEN}Entering Intent Classifier")
        print("--------------------------------")

        message = state.get("user_message", "").strip()

        # HARD RULE: numeric detection
        if message.replace(".", "", 1).isdigit():
            state["intent"] = WhatsappMessageIntent.COUNTER_OFFER
            state["user_offer"] = float(message)
            state["next_action"] = NextAction.ESCALATE_NEGOTIATION
            return state

        # LLM classification
        result = await Runner.run(
            Agent(
                name="analyze_whatsapp_message",
                instructions=ANALYZE_INFLUENCER_WHATSAPP_PROMPT,
                output_type=AnalyzeMessageOutput,
            ),
            input=message,
        )

        analysis = result.final_output or {}
        intent = analysis.get("intent", WhatsappMessageIntent.UNCLEAR)

        state["analysis"] = analysis
        state["intent"] = intent
        state["next_action"] = analysis.get(
            "next_action", NextAction.GENERATE_CLARIFICATION
        )

    except Exception as e:
        print(f"{Colors.RED} Intent Error: {e}")
        state["intent"] = WhatsappMessageIntent.UNCLEAR
        state["next_action"] = NextAction.GENERATE_CLARIFICATION

    return state
