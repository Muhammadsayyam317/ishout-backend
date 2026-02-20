import resend
from typing import List, Dict
from app.config.credentials_config import config
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Use FRONTEND_URL from .env
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Resend API key
resend.api_key = config.RESEND_API_KEY

VERIFICATION_EMAIL_TEMPLATE_HTML = """
<h2>Verify Your Email 🎉</h2>
<p>Hi {company_name},</p>

<p>
Thank you for registering on <strong>Ishout</strong>.
Please verify your email by clicking the button below:
</p>

<p style="margin: 24px 0;">
  <a href="{verification_link}"
     style="background-color:#000;color:#fff;padding:12px 20px;text-decoration:none;border-radius:6px;font-weight:600;">
    Verify Email
  </a>
</p>

<p>
This link will expire in 1 hour.
</p>

<p>
Best regards,<br />
<strong>The Ishout Team</strong>
</p>
"""

def send_verification_email(
    to: List[str],
    subject: str,
    company_name: str,
    token: str,  
) -> Dict:
 
    verification_link = f"{FRONTEND_URL}/auth/verify-email?token={token}"

    html = VERIFICATION_EMAIL_TEMPLATE_HTML.format(
        company_name=company_name,
        verification_link=verification_link,
    )

    return resend.Emails.send(
        {
            "from": config.RESEND_FROM_EMAIL,
            "to": to,
            "subject": subject,
            "html": html,
        }
    )