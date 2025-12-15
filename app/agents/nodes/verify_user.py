from fastapi import HTTPException
from app.config import config
from app.db.connection import get_db
from app.services.whatsapp.onboarding_Whatsapp_message import send_whatsapp_message
from app.utils.helpers import normalize_phone


async def node_verify_user(state):
    try:
        user_phoneNumber = state.get("sender_id")
        print(f"user phone number from state: {user_phoneNumber}")

        user_phoneNumber = normalize_phone(user_phoneNumber)
        db = get_db()
        users_collection = db.get_collection(config.MONGODB_ATLAS_COLLECTION_USERS)
        user = await users_collection.find_one({"phone": user_phoneNumber})

        if not user:
            print(
                f"[node_verify_user] User not found for phone number: {user_phoneNumber}"
            )
            state["is_existing_user"] = False
            state["reply"] = (
                f"Hi {state.get('contact_person')}! It looks like you are not registered with iShout.\n\n"
                "Please create an account to continue: https://ishout.vercel.app/auth/register"
            )

            state["reply_sent"] = False
            await send_whatsapp_message(user_phoneNumber, state["reply"])
            state["reply_sent"] = True
            return state

        state["is_existing_user"] = True
        state["contact_person"] = user.get("contact_person")
        state["company_name"] = user.get("company_name")
        state["user_status"] = user.get("status")
        state["name"] = (
            state.get("name") or user.get("contact_person") or user.get("company_name")
        )
        return state

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error verifying user: {str(e)}"
        ) from e
