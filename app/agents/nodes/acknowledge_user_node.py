async def node_acknowledge_user(state):
    print("Entering node_acknowledge_user")
    try:
        if state.get("acknowledged"):
            print("acknowledged missing in state")
            state["reply"] = (
                "🎉 *Campaign Created Successfully!*\n\n"
                f"📱 Platform: {', '.join(state['platform'])}\n"
                f"🎯 Category: {', '.join(state['category'])}\n"
                f"🌍 Location: {', '.join(state['country'])}\n"
                f"👥 Followers: {', '.join(state['followers'])}\n"
                f"🔢 Influencers: {state['limit']}\n\n"
                "We'll notify you once influencers are shortlisted!"
            )
            print(f"Reply to user is: {state['reply']}")
            state["reply_sent"] = False
            state["acknowledged"] = True
            state["done"] = True
            print("Exiting node_acknowledge_user successfully")
            return state
    except Exception:
        print("❌ Error in node_acknowledge_user")
        state["reply"] = None
        state["done"] = True
        print("Exiting node_acknowledge_user with error")
        return state
