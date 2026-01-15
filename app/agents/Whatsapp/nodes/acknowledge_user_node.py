async def node_acknowledge_user(state):
    print("Entering node_acknowledge_user")
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

        print("Exiting node_acknowledge_user successfully")
        return state

    except Exception as e:
        print("❌ Error in node_acknowledge_user:", e)
        state["done"] = True
        return state
