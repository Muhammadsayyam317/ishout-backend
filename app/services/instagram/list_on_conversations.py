import requests
from app.config.credentials_config import config


async def instagram_conversations_list() -> dict:
    url = f"https://graph.facebook.com/v9.0/{config.IG_BUSINESS_ID}/conversations?platform=instagram"
    params = {
        "access_token": config.INSTAGRAM_PAGE_ACCESS_TOKEN,
        "fields": "id,created_time,from,to,participants,messages.limit(100).order(chronological)",
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data


async def instagram_conversation_messages(conversation_id: str) -> dict:
    url = f"https://graph.facebook.com/v24.0/{conversation_id}/messages"
    params = {
        "access_token": config.INSTAGRAM_PAGE_ACCESS_TOKEN,
        "fields": "id,created_time,from,to,message",
    }
    response = requests.get(url, params=params)
    return response.json()
