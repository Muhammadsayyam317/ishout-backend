from agents import Agent, Runner
from agents.agent_output import AgentOutputSchema

from app.Guardails.input_guardrails import InstagramInputGuardrail
from app.Guardails.output_guardrails import InstagramOutputGuardrail
from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.core.exception import InternalServerErrorException
from app.utils.prompts import NEGOTIATE_INFLUENCER_DM_PROMPT

generate_reply_agent = Agent(
    name="generate_reply",
    instructions=NEGOTIATE_INFLUENCER_DM_PROMPT,
    input_guardrails=[InstagramInputGuardrail],
    output_guardrails=[InstagramOutputGuardrail],
    output_type=AgentOutputSchema(InstagramConversationState, strict_json_schema=False),
)


async def node_generate_reply(
    state: InstagramConversationState,
) -> InstagramConversationState:
    print("Entering into Reply Generation Node")
    try:
        print(f"Generating reply for: {state.user_message}")

        result = await Runner.run(
            generate_reply_agent,
            input={
                "thread_id": state.thread_id,
                "user_message": state.user_message,
                "brand_intent": state.brand_intent,
                "pricing_mentioned": state.pricing_mentioned,
                "negotiation_stage": state.negotiation_stage.value,
                "negotiation_strategy": state.negotiation_strategy.value,
            },
        )

        output: InstagramConversationState = result.final_output

        if not output.final_reply:
            raise ValueError("Empty reply from generate_reply agent")

        state.ai_draft = output.final_reply
        state.final_reply = output.final_reply
        print("Exiting from Reply Generation Node")
        return state

    except Exception as e:
        raise InternalServerErrorException(
            message=f"Instagram reply generation failed: {str(e)}"
        )
