import json

from agents import Agent, Runner
from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.Schemas.instagram.negotiation_schema import AnalyzeMessageOutput, NextAction
from app.Guardails.input_guardrails import WhatsappInputGuardrail
from app.utils.prompts import ANALYZE_INFLUENCER_WHATSAPP_PROMPT
from app.utils.printcolors import Colors
from app.utils.message_context import get_history_list


async def intentclassifier(state: WhatsappNegotiationState, checkpointer=None):
    print(f"{Colors.GREEN}Entering intentclassifier node")
    user_message = state.get("user_message", "")
    history = get_history_list(state)

    # Pass a JSON string so the agents library (which may treat input as list) does not fail.
    # The prompt tells the model to parse this JSON for "history" and "latest_user_message".
    analyzer_input_str = json.dumps(
        {"history": history, "latest_user_message": user_message},
        default=str,
    )

    result = await Runner.run(
        Agent(
            name="analyze_whatsapp_message",
            instructions=ANALYZE_INFLUENCER_WHATSAPP_PROMPT,
            input_guardrails=[WhatsappInputGuardrail],
            output_type=AnalyzeMessageOutput,
        ),
        input=analyzer_input_str,
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
