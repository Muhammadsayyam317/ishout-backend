from agents import Agent, Runner
from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.Schemas.instagram.negotiation_schema import AnalyzeMessageOutput, NextAction
from app.Guardails.input_guardrails import WhatsappInputGuardrail
from app.utils.prompts import ANALYZE_INFLUENCER_WHATSAPP_PROMPT
from app.utils.printcolors import Colors


async def intentclassifier(state: WhatsappNegotiationState, checkpointer):
    thread_id = state.get("thread_id")
    print(f"{Colors.GREEN}Entering intentclassifier node")
    print("--------------------------------")

    user_message = state.get("user_message", "")

    # Run AI to analyze intent
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

    # Update state
    state["analysis"] = analysis
    state["intent"] = intent
    state["next_action"] = analysis.get(
        "next_action", NextAction.GENERATE_CLARIFICATION
    )

    # Save last analysis in Redis for 5 min
    await checkpointer.save_checkpoint(
        key=f"negotiation:{thread_id}:analysis", value=analysis, ttl=300
    )

    print(
        f"{Colors.CYAN}IntentClassifier Result → Intent: {intent}, NextAction: {state['next_action']}"
    )
    print(f"{Colors.YELLOW}Exiting intentclassifier node")
    print("--------------------------------")
    return state
