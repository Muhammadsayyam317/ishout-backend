from agents import Agent, Runner
from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.Schemas.instagram.negotiation_schema import AnalyzeMessageOutput, NextAction
from app.Guardails.input_guardrails import WhatsappInputGuardrail
from app.utils.prompts import ANALYZE_INFLUENCER_WHATSAPP_PROMPT
from app.utils.printcolors import Colors


async def intentclassifier(state: WhatsappNegotiationState, checkpointer=None):
    print(f"{Colors.GREEN}Entering intentclassifier node")
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
    intent = analysis.get("intent", "unclear")

    # Persist full analysis
    state["analysis"] = analysis
    state["intent"] = intent
    state["next_action"] = analysis.get(
        "next_action", NextAction.GENERATE_CLARIFICATION
    )

    # Capture influencer's offered rate (if any) into user_offer
    budget = analysis.get("budget_amount")
    if budget is not None:
        try:
            state["user_offer"] = float(budget)
        except (TypeError, ValueError):
            # Leave user_offer as-is if parsing fails
            pass
    print(
        f"{Colors.CYAN}IntentClassifier Result → Intent: {intent}, NextAction: {state['next_action']}, UserOffer: {state.get('user_offer')}"
    )
    return state
