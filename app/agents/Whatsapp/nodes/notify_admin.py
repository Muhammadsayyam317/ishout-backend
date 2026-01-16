from app.config.credentials_config import config
from app.services.whatsapp.onboarding_message import send_whatsapp_message


async def node_notify_admin_campaign_created(campaign, user):
    print("Entering into node_notify_admin_campaign_created")
    try:
        print(f"Campaign: {campaign} User: {user}")
        message = (
            "🚨 *New Campaign Created*\n\n"
            f"🏢 Company: {user.get('company_name')}\n"
            f"👤 Contact: {user.get('contact_person')}\n"
            f"📞 Phone: {user.get('phone')}\n"
            f"📱 Platform: {', '.join(campaign['platform'])}\n"
            f"🎯 Category: {', '.join(campaign['category'])}\n"
            f"🌍 Country: {', '.join(campaign['country'])}\n"
            f"👥 Followers: {', '.join(campaign['followers'])}\n"
            f"🔢 Influencers: {campaign['limit']}\n"
            f"📌 Status: PENDING"
        )
        print("Message: ", message)
        success = await send_whatsapp_message(config.ADMIN_PHONE, message)
        print(f"Success: {success}")
        if not success:
            raise Exception("Failed to send message to admin")
        print("Exiting from notify_admin_campaign_created")
        print(f"Success: {success}")
        return True
    except Exception as e:
        print("❌ Error in notify_admin_campaign_created:", e)
        return False
