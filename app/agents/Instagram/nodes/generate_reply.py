from agents import Agent, Runner
from agents.agent_output import AgentOutputSchema
from app.Schemas.instagram.message_schema import GenerateReplyOutput
from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.core.exception import InternalServerErrorException
from app.utils.prompts import NEGOTIATE_INFLUENCER_DM_PROMPT


generate_reply_agent = Agent(
    name="generate_reply",
    instructions=NEGOTIATE_INFLUENCER_DM_PROMPT,
    model="gpt-4o-mini",
    output_type=AgentOutputSchema(GenerateReplyOutput, strict_json_schema=False),
)


async def GenerateReply(message: str) -> GenerateReplyOutput:
    try:
        print(f"Generating reply for: {message}")
        result = await Runner.run(
            generate_reply_agent,
            input=message,
        )
        output: GenerateReplyOutput = result.final_output
        print(f"Output from Generate Reply Node: {output}")
        return output
    except Exception as e:
        raise InternalServerErrorException(f"Error generating reply: {str(e)}")


async def generate_reply_node(
    state: InstagramConversationState,
) -> InstagramConversationState:
    print("✍️ LangGraph: Generate reply node")

    reply = await GenerateReply(message=state.user_message)
    print(f"Reply from Generate Reply Node: {reply}")
    return InstagramConversationState(
        **state.model_dump(), final_reply=reply.final_reply
    )
