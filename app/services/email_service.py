from app.config import config
import resend
from typing import Dict, List

WELCOME_EMAIL_TEMPLATE_HTML = """
<h2>Welcome to Ishout 🎉</h2>
<p>Hi there,</p>
<p>
We’re excited to have you on board! Your company account has been successfully created on
<strong>Ishout</strong> — the platform that helps brands discover, evaluate, and collaborate with
the right influencers effortlessly.
</p>
<p>With Ishout, you can:</p>
<ul>
  <li>🔍 Discover relevant influencers for your campaigns</li>
  <li>📊 Review influencer profiles and performance insights</li>
  <li>✅ Approve or reject influencers directly from your dashboard or WhatsApp</li>
  <li>🚀 Manage campaigns faster and smarter</li>
</ul>
<p>You can log in to your account using the button below:</p>
<p style="margin: 24px 0;">
  <a href="https://www.ishout.com"
     style="background-color:#000;color:#fff;padding:12px 20px;text-decoration:none;border-radius:6px;font-weight:600;">
    Login to Ishout
  </a>
</p>
<p>
If you have any questions or need help getting started, feel free to reply to this email.
</p>
<p>
Best regards,<br />
<strong>The Ishout Team</strong>
</p>
"""


def send_welcome_email(to: List[str], subject: str, html: str) -> Dict:
    params: resend.Emails.SendParams = {
        "from": config.RESEND_FROM_EMAIL,
        "to": to,
        "subject": subject,
        "html": WELCOME_EMAIL_TEMPLATE_HTML,
    }
    email: resend.Email = resend.Emails.send(params)
    return email
