from agents import Agent, AgentOutputSchema
from app.Guardails.input_guardrails import InstagramInputGuardrail
from app.Guardails.output_guardrails import InstagramOutputGuardrail
from app.utils.clients import get_openai_client
from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.utils.prompts import NEGOTIATE_INFLUENCER_DM_PROMPT
from app.core.exception import InternalServerErrorException


openai_client = get_openai_client()

generate_reply_agent = Agent(
    name="generate_reply",
    instructions=NEGOTIATE_INFLUENCER_DM_PROMPT,
    input_guardrails=[InstagramInputGuardrail],
    output_guardrails=[InstagramOutputGuardrail],
    output_type=AgentOutputSchema(InstagramConversationState, strict_json_schema=False),
)


async def node_generate_reply(state: InstagramConversationState):
    try:
        print(f"Generating reply for: {state.user_message}")
        prompt = NEGOTIATE_INFLUENCER_DM_PROMPT.format(
            user_message=state.user_message,
            brand_intent=state.brand_intent or "",
            negotiation_stage=state.negotiation_stage.value,
            negotiation_strategy=state.negotiation_strategy.value,
        )

        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": NEGOTIATE_INFLUENCER_DM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
            max_tokens=300,
            metadata={
                "thread_id": state.thread_id,
                "platform": "INSTAGRAM",
                "negotiation_strategy": state.negotiation_strategy.value,
                "brand_intent": state.brand_intent,
                "pricing_mentioned": state.pricing_mentioned,
            },
        )

        print(f"Reply: {response.choices[0].message.content}")
        reply = response.choices[0].message.content.strip()
        if not reply:
            raise ValueError("Empty LLM response")
        print(f"Reply: {reply}")
        state.ai_draft = reply
        state.final_reply = reply
        return state

    except Exception as e:
        raise InternalServerErrorException(
            message=f"Instagram reply generation failed: {str(e)}"
        )
