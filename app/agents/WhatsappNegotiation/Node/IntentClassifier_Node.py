from app.Schemas.instagram.negotiation_schema import AnalyzeMessageOutput, NextAction
from app.Schemas.whatsapp.negotiation_schema import (
    WhatsappMessageIntent,
    WhatsappNegotiationState,
)
from agents import Agent, Runner
from app.Guardails.input_guardrails import WhatsappInputGuardrail
from app.utils.printcolors import Colors
from app.utils.prompts import ANALYZE_INFLUENCER_WHATSAPP_PROMPT


async def intentclassifier(state: WhatsappNegotiationState):
    try:
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

        analysis: AnalyzeMessageOutput = result.final_output or {}
        intent = analysis.get("intent", WhatsappMessageIntent.UNCLEAR)

        # Update state
        state["analysis"] = analysis
        state["intent"] = intent
        state["next_action"] = analysis.get(
            "next_action", NextAction.GENERATE_CLARIFICATION
        )

        print(
            f"{Colors.CYAN}IntentClassifier Result → Intent: {intent}, NextAction: {state['next_action']}"
        )
        print(f"{Colors.YELLOW}Exiting intentclassifier node")
        print("--------------------------------")

    except Exception as e:
        print(f"{Colors.RED}[intentclassifier] Error: {e}")
        state["intent"] = WhatsappMessageIntent.UNCLEAR
        state["next_action"] = NextAction.GENERATE_CLARIFICATION
        state["analysis"] = {}

    return state
