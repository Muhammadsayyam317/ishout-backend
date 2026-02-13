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
        print("Intent Classifier Result:", analysis)
        intent = analysis.get("intent", WhatsappMessageIntent.UNCLEAR)
        if intent not in WhatsappMessageIntent.__members__.values():
            intent = WhatsappMessageIntent.UNCLEAR

        state["analysis"] = analysis
        state["intent"] = intent
        state["next_action"] = analysis.get(
            "next_action", NextAction.GENERATE_CLARIFICATION
        )

        print(f"Intent: {state['intent']}")
        print(f"Next Action: {state['next_action']}")
        print("f{Colors.RED} Exiting from intent Classifier")

    except Exception as e:
        print("Error in intentclassifier:", e)
        state["intent"] = WhatsappMessageIntent.UNCLEAR
        state["next_action"] = NextAction.GENERATE_CLARIFICATION
        state["analysis"] = {}

    return state
