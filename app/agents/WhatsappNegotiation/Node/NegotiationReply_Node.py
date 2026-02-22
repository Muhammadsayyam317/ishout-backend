from agents import Agent, Runner
from agents.agent_output import AgentOutputSchema
from app.Guardails.input_guardrails import WhatsappInputGuardrail
from app.Schemas.instagram.negotiation_schema import GenerateReplyOutput
from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.utils.printcolors import Colors


NEGOTIATE_INFLUENCER_DM_PROMPT = "Generate a professional WhatsApp reply based on conversation history: {state.get('history', [])} and user message: {state.get('user_message')}"


async def generate_reply_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering generate_reply_node")
    print("--------------------------------")

    prompt = f"Generate a professional WhatsApp reply based on conversation history: {state.get('history', [])} and user message: {state.get('user_message')}"
    result = await Runner.run(
        Agent(
            name="ai_generate_reply",
            instructions=prompt,
            input_guardrails=[WhatsappInputGuardrail],
            output_type=AgentOutputSchema(
                GenerateReplyOutput, strict_json_schema=False
            ),
        ),
        input=state.get("history", []),
    )

    ai_message = result.final_output.get(
        "final_reply", "Thanks for your message. We'll get back shortly."
    )
    state["final_reply"] = ai_message
    state.setdefault("history", []).append({"sender_type": "AI", "message": ai_message})

    print(f"{Colors.CYAN}Generated AI Reply: {ai_message}")
    print(f"{Colors.YELLOW}Exiting generate_reply_node")
    print("--------------------------------")
    return state
