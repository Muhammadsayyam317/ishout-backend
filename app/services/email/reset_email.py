import json
import jwt
import resend
from app.config.credentials_config import config
from datetime import datetime, timezone, timedelta


RESET_EMAIL_TEMPLATE_HTML = """
<h2>Reset your password</h2>
<p>Hi there,</p>
<p>
We've received a request to reset your password. You can do this by clicking the button below.
</p>
<p>
<a href="https://www.ishout.com/reset-password">Reset your password</a>
</p>
<p>
If you didn't request a password reset, please ignore this email.
</p>
<p>
Best regards,<br />
<strong>The Ishout Team</strong>
</p>
</p>
"""


def create_reset_password_token(email: str):
    expiry_time = datetime.now(timezone.utc) + timedelta(minutes=10)
    data = {"sub": email, "exp": expiry_time}
    token = jwt.encode(data, config.JWT_SECRET_KEY, config.JWT_ALGORITHM)
    return {
        "token": token,
        "forget_url_link": f"{config.FRONTEND_URL}/auth/reset-password?token={token}",
        "expiry_time": expiry_time,
    }


resend.api_key = config.RESEND_API_KEY


def send_reset_email(to: str, body: dict) -> resend.Email:
    params: resend.Emails.SendParams = {
        "from": config.RESEND_FROM_EMAIL,
        "to": [to],
        "subject": "Reset your password",
        "html": RESET_EMAIL_TEMPLATE_HTML.format(
            company_name=body["company_name"],
            forget_url_link=f"<a href='{body['forget_url_link']}'>Reset your password</a>",
            expiry_time=datetime.strftime(body["expiry_time"], "%Y-%m-%d %H:%M:%S"),
        ),
    }
    email: resend.Email = resend.Emails.send(params)
    return email
