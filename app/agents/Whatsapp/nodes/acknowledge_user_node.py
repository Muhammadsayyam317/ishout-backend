from app.utils.printcolors import Colors


async def node_acknowledge_user(state):
    print(f"{Colors.GREEN}Entering into node_acknowledge_user")
    print("--------------------------------")
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
        state["reset_after_reply"] = True
        print(f"{Colors.YELLOW}Exiting from node_acknowledge_user")
        print("--------------------------------")
        print(f"{Colors.CYAN}State: {state}")
        print("--------------------------------")
        return state

    except Exception as e:
        state["done"] = True
        print("Error in node_acknowledge_user")
        print("--------------------------------")
        print(f"{Colors.RED}Error in node_acknowledge_user: {e}")
        print("--------------------------------")
        return state
