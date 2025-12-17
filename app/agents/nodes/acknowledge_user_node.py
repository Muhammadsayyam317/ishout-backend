async def node_acknowledge_user(state):
    if not state.get("acknowledged"):
        state["reply"] = (
            "🎉 *Campaign Created Successfully!*\n\n"
            f"📱 Platform: {', '.join(state['platform'])}\n"
            f"🎯 Category: {', '.join(state['category'])}\n"
            f"🌍 Location: {', '.join(state['country'])}\n"
            f"👥 Followers: {', '.join(state['followers'])}\n"
            f"🔢 Influencers: {state['limit']}\n\n"
            "We'll notify you once influencers are shortlisted!"
        )
        state["reply_sent"] = False
        state["acknowledged"] = True
        state["done"] = True
    return state
