from typing import Dict, Any
import json
import openai
from app.config import config

async def check_input_guard_rail(input_text: str) -> Dict[str, bool]:
    """
    Check if the user input is related to finding influencers
    
    Args:
        input_text: The user's input text
        
    Returns:
        Dict with tripwire flag
    """
    try:
        # Create a system message that describes the task
        system_msg = ("Check if the user input is about finding influencers. "
                     "If not, politely respond that the input is not relevant.")
        
        # Call the OpenAI API - newer versions don't need await for this call
        client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": input_text}
            ],
            tools=[{
                "type": "function",
                "function": {
                    "name": "is_related_to_influencers",
                    "description": "Determines if the input is related to finding influencers",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "isRelatedToInfluencers": {
                                "type": "boolean",
                                "description": "Whether the input is related to finding influencers"
                            }
                        },
                        "required": ["isRelatedToInfluencers"]
                    }
                }
            }],
            tool_choice={"type": "function", "function": {"name": "is_related_to_influencers"}}
        )
        
        # Extract the result from the tool calls (updated API format)
        tool_calls = response.choices[0].message.tool_calls
        if tool_calls and len(tool_calls) > 0 and tool_calls[0].function.name == "is_related_to_influencers":
            result = json.loads(tool_calls[0].function.arguments)
            return {"tripwire": not result.get("isRelatedToInfluencers", False)}
        
        return {"tripwire": True}  # Default to true if something went wrong
    except Exception as e:
        # In case of error, let the input through
        return {"tripwire": False}