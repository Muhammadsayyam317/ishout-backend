async def node_acknowledge_user(state):
    try:
        if state.get("acknowledged"):
            return state

        state["reply"] = (
            "🎉 *Campaign Created Successfully!*\n\n"
            f"📱 Platform: {', '.join(state.get('platform', []))}\n"
            f"🎯 Category: {', '.join(state.get('category', []))}\n"
            f"🌍 Location: {', '.join(state.get('country', []))}\n"
            f"👥 Followers: {', '.join(state.get('followers', []))}\n"
            f"🔢 Influencers: {state.get('limit')}\n\n"
            "✅ Our team has received your request.\n"
            "📢 We’ll notify you once influencers are shortlisted!"
        )
        state["reply_sent"] = False
        state["acknowledged"] = True
        state["done"] = True
        return state

    except Exception:
        state["done"] = True
        return state
