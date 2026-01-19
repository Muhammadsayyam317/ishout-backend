from app.config import config
from app.db.connection import get_db
from app.utils.helpers import normalize_phone


async def node_verify_user(state):
    try:
        sender_id = state.get("sender_id")
        if not sender_id:
            raise ValueError("sender_id missing in state")
        user_phoneNumber = normalize_phone(sender_id)
        db = get_db()
        users_collection = db.get_collection(config.MONGODB_ATLAS_COLLECTION_USERS)
        user = await users_collection.find_one({"phone": user_phoneNumber})

        # unregistered user
        if not user:
            state["is_existing_user"] = False
            state["reply"] = (
                "You are not registered with iShout.\n\n"
                "Please create an account to continue:\n"
                f"{config.REGISTER_URL}"
            )
            state["reply_sent"] = False
            state["done"] = True
            return state

        # Existing user
        state["is_existing_user"] = True
        state["name"] = user.get("contact_person") or user.get("company_name")
        state["reply"] = (
            f"Hi {state['name']}, you’re verified with iShout.\n\n"
            "Tell us what kind of influencers you’re looking for."
        )
        state["reply_sent"] = False
        return state

    except Exception:
        state["is_existing_user"] = False
        state["reply"] = (
            "Sorry, we couldn't verify your account right now.\n\n"
            "Please try again later or contact iShout support."
        )
        state["reply_sent"] = False
        state["done"] = True
        return state
