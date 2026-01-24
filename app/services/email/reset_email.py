import resend
from datetime import datetime
from app.config.credentials_config import config

verify_otp_url = config.VERIFY_OTP_URL

RESET_EMAIL_TEMPLATE_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Reset Your Password</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f6f8;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td align="center" style="padding:30px;">
        <table width="100%" max-width="600px" style="background:#ffffff;border-radius:8px;padding:30px;">

          <!-- Header -->
          <tr>
            <td align="center" style="padding-bottom:20px;">
              <h2 style="color:#111827;margin:0;">Reset Your Password</h2>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="color:#374151;font-size:15px;line-height:22px;">
              <p>Hello,</p>
              <p>
                We received a request to reset your password for your 
                <strong>iShout</strong> account.
              </p>

              <p>
                Use the following One-Time Password (OTP) to continue:
              </p>

              <!-- OTP Box -->
              <div style="
                text-align:center;
                font-size:28px;
                letter-spacing:6px;
                font-weight:bold;
                color:#111827;
                background:#f3f4f6;
                padding:15px;
                border-radius:6px;
                margin:20px 0;
              ">
                {otp}
              </div>
              <p style="font-size:14px;color:#6b7280;">
                This OTP will expire in <strong>5 minutes</strong>. If you did not request a password reset, you can safely ignore this email.
              </p>

              <p style="margin-top:30px;">
                Regards,<br/>
                <strong>The Ishout Team</strong>
              </p>
            </td>
          </tr>

        </table>

        <!-- Footer -->
        <p style="font-size:12px;color:#9ca3af;margin-top:15px;">
          © {year} Ishout. All rights reserved.
        </p>
      </td>
    </tr>
  </table>
</body>
</html>
"""


resend.api_key = config.RESEND_API_KEY


def send_reset_email(to: str, otp: str) -> resend.Email:
    html_content = RESET_EMAIL_TEMPLATE_HTML.format(
        otp=otp,
        verify_otp_url=config.VERIFY_OTP_URL,
        year=datetime.now().year,
    )

    return resend.Emails.send(
        {
            "from": config.RESEND_FROM_EMAIL,
            "to": [to],
            "subject": "Reset Your Password – Ishout",
            "html": html_content,
        }
    )
