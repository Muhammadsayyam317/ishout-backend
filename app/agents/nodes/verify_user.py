from app.config import config
from app.db.connection import get_db
from app.utils.helpers import normalize_phone


async def node_verify_user(state):
    user_phoneNumber = normalize_phone(state.get("sender_id"))

    db = get_db()
    users_collection = db.get_collection(config.MONGODB_ATLAS_COLLECTION_USERS)
    user = await users_collection.find_one({"phone": user_phoneNumber})

    if not user:
        state["is_existing_user"] = False
        state["reply"] = (
            "You are not registered with iShout.\n\n"
            "Please create an account to continue: https://ishout.vercel.app/auth/register"
        )
        state["reply_sent"] = False
        return state

    state["is_existing_user"] = True
    state["name"] = user.get("contact_person") or user.get("company_name")

    state["reply"] = (
        f"Hi {state['name']}, you’re verified with iShout.\n\n"
        "Tell us what kind of influencers you’re looking for."
    )
    state["reply_sent"] = False

    return state
