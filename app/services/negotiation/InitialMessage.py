import httpx
from pymongo.collection import ObjectId
from app.config.credentials_config import config
from app.db.connection import get_db
from app.services.whatsapp.save_negotiation_message import save_negotiation_message
from app.utils.Enums.user_enum import SenderType
from bson.errors import InvalidId
from datetime import datetime, timezone
from app.agents.WhatsappNegotiation.state.negotiation_state import (
    update_negotiation_state,
)
from app.utils.printcolors import Colors


INITIAL_OUTREACH_MESSAGE = (
    "Hi this is the collaboration team from iShout.\n\n"
    "We'd love to work with you on an upcoming campaign that matches your profile.\n\n"
    "Just reply 'interested,' and we will share the campaign brief and next steps."
)


async def NegotiationInitialMessage(influencer_id: str):
    print(f"{Colors.GREEN}Entering into NegotiationInitialMessage for influencer_id: {influencer_id}")
    print("--------------------------------")
    db = get_db()
    collection = db.get_collection("campaign_influencers")
    try:
        influencer_object_id = ObjectId(influencer_id)
    except InvalidId:
        return {"status": "error", "message": "Invalid influencer_id"}
    influencer = await collection.find_one({"_id": influencer_object_id})
    if not influencer:
        return {"status": "error", "message": "Influencer not found"}

    influencer_name = influencer.get("username")
    phone_number = influencer.get("phone_number")

    if not phone_number:
        return {"status": "error", "message": "Influencer has no phone number"}

    headers = {
        "Authorization": f"Bearer {config.META_WHATSAPP_ACCESSSTOKEN}",
        "Content-Type": "application/json",
    }

    payload_meta = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "template",
        "template": {
            "name": "negotiation",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": influencer_name},
                    ],
                }
            ],
        },
    }
    print(f"{Colors.CYAN}Sending WhatsApp message to: {phone_number}")
    print("--------------------------------")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(
                "https://graph.facebook.com/v22.0/967002123161751/messages",
                headers=headers,
                json=payload_meta,
            )
        print(f"{Colors.GREEN}WhatsApp message sent successfully")
        print("--------------------------------")
    except Exception as e:
        print(f"{Colors.RED} Error sending WhatsApp message: {e}")
        return {"status": "error", "message": f"Error sending WhatsApp message: {e}"}

    await save_negotiation_message(
        thread_id=phone_number,
        username=influencer_name,
        sender=SenderType.AI.value,
        message=INITIAL_OUTREACH_MESSAGE,
        agent_paused=False,
        human_takeover=False,
        conversation_mode="NEGOTIATION",
    )
    # Create Negotiation Control Record with fresh history containing the initial outreach
    await update_negotiation_state(
        thread_id=phone_number,
        data={
            "thread_id": phone_number,
            "influencer_id": influencer_id,
            "analysis": {},
            "final_reply": None,
            "intent": None,
            "next_action": None,
            "min_price": None,
            "max_price": None,
            "last_offered_price": None,
            "negotiation_round": 0,
            "negotiation_status": None,
            "manual_negotiation": False,
            "user_offer": None,
            "negotiation_completed": False,
            "conversation_mode": "NEGOTIATION",
            "agent_paused": False,
            "human_takeover": False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "history": [
                {"sender_type": "AI", "message": INITIAL_OUTREACH_MESSAGE},
            ],
        },
    )

    print(
        f"{Colors.YELLOW}Negotiation Initial Message sent successfully and Negotiation Control Record created successfully"
    )
    print("--------------------------------")
    return {
        "status": "success",
        "message": "Negotiation Initial Message sent successfully",
    }
