import re
from fastapi import HTTPException
from app.db.connection import get_db


def _normalize_phone(phone: str | None) -> str:
    return re.sub(r"[^\d]", "", phone or "")


async def node_verify_user(state, config):
    try:
        user_phoneNumber = state.get("sender_id")
        print(f"user phone number from state: {user_phoneNumber}")

        user_phoneNumber = _normalize_phone(user_phoneNumber)
        db = get_db()
        users_collection = db.get_collection("users")
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
