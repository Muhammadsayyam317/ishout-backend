from app.config.credentials_config import config
from app.services.whatsapp.onboarding_message import send_whatsapp_message


async def node_notify_admin_campaign_created(campaign, user):
    try:
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

        success = await send_whatsapp_message(config.ADMIN_PHONE, message)
        if not success:
            raise Exception("Failed to send message to admin")
        return True
    except Exception:
        return False
