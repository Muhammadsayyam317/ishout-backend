from agents import Agent, AgentOutputSchema
from openai import OpenAI
from app import config
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
    print(f"Generating reply for: {state.user_message}")
    try:
        prompt = NEGOTIATE_INFLUENCER_DM_PROMPT.format(
            user_message=state.user_message,
            brand_intent=state.brand_intent or "",
            negotiation_stage=state.negotiation_stage.value,
            negotiation_strategy=state.negotiation_strategy.value,
        )

        response = await OpenAI(
            api_key=config.OPENAI_API_KEY,
            model="gpt-4o-mini",
        ).chat.completions.create(
            messages=[
                {"role": "system", "content": NEGOTIATE_INFLUENCER_DM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
            max_tokens=300,
            metadata={
                "thread_id": str(state.thread_id),
                "platform": "INSTAGRAM",
                "negotiation_strategy": str(state.negotiation_strategy.value),
                "brand_intent": str(state.brand_intent or ""),
                "pricing_mentioned": str(state.pricing_mentioned or ""),
            },
        )

        print(f"Reply: {response.choices[0].message.content}")
        reply = response.choices[0].message.content.strip()
        if not reply:
            raise ValueError("Empty LLM response")
        print(f"Generated Reply: {reply}")
        state.ai_draft = reply
        state.final_reply = reply
        print("Exiting from Reply Generation")
        return state

    except Exception as e:
        raise InternalServerErrorException(
            message=f"Instagram reply generation failed: {str(e)}"
        )
