import resend
from app.config.credentials_config import config


RESET_EMAIL_TEMPLATE_HTML = """
<h2>Reset your password</h2>
<p>Hi there,</p>
<p>
We've received a request to reset your password. You can do this by clicking the button below.
</p>
<p>
<a href="https://www.ishout.com/auth/reset-passwordo">Reset your password</a>
</p>
<p>OTP: {otp}</p>
<p>
If you didn't request a password reset, please ignore this email.
</p>
<p>
Best regards,<br />
<strong>The Ishout Team</strong>
</p>
</p>
"""


resend.api_key = config.RESEND_API_KEY


def send_reset_email(to: str, body: dict, otp: str) -> resend.Email:
    params: resend.Emails.SendParams = {
        "from": config.RESEND_FROM_EMAIL,
        "to": [to],
        "subject": "Reset your password",
        "html": RESET_EMAIL_TEMPLATE_HTML.format(
            company_name=body["company_name"],
            forget_url_link=f"<a href='{body['forget_url_link']}'>Reset your password</a>",
            otp=otp,
        ),
    }
    email: resend.Email = resend.Emails.send(params)
    return email
