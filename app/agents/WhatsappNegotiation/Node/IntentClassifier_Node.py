from app.Schemas.instagram.negotiation_schema import (
    AnalyzeMessageOutput,
    NextAction,
)
from agents import Agent, Runner
from app.Guardails.input_guardrails import (
    WhatsappInputGuardrail,
)
from app.Schemas.whatsapp.negotiation_schema import (
    WhatsappMessageIntent,
    WhatsappNegotiationState,
)
from app.utils.printcolors import Colors
from app.utils.prompts import (
    ANALYZE_INFLUENCER_WHATSAPP_PROMPT,
)


async def intentclassifier(state: WhatsappNegotiationState):
    try:
        print(f"{Colors.GREEN}Entering Intent Classifier")
        print("--------------------------------")
        result = await Runner.run(
            Agent(
                name="analyze_whatsapp_message",
                instructions=ANALYZE_INFLUENCER_WHATSAPP_PROMPT,
                input_guardrails=[WhatsappInputGuardrail],
                output_type=AnalyzeMessageOutput,
            ),
            input=state.get("user_message", ""),
        )

        analysis: AnalyzeMessageOutput = result.final_output or {}
        print(f"{Colors.CYAN}Intent Classifier Result: {analysis}")

        intent = analysis.get("intent", WhatsappMessageIntent.UNCLEAR)
        budget = analysis.get("budget_amount")
        next_action = analysis.get("next_action", NextAction.GENERATE_CLARIFICATION)

        # Normalize next_action for negotiation intents
        if intent in (
            WhatsappMessageIntent.INTEREST,
            WhatsappMessageIntent.NEGOTIATE,
            WhatsappMessageIntent.ACCEPT,
        ):
            if budget:
                next_action = NextAction.ASK_RATE
            else:
                next_action = NextAction.GENERATE_CLARIFICATION

        state["analysis"] = analysis
        state["intent"] = intent
        state["next_action"] = next_action

        print(f"Intent: {intent}")
        print(f"Budget Amount: {budget}")
        print(f"Next Action: {next_action}")
        print(f"{Colors.YELLOW}Exiting from intentclassifier")
        print("--------------------------------")

    except Exception as e:
        print(f"{Colors.RED}Error in intentclassifier: {e}")
        state["intent"] = WhatsappMessageIntent.UNCLEAR
        state["next_action"] = NextAction.GENERATE_CLARIFICATION
        state["analysis"] = {}

    return state
