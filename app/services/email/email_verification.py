import resend
from typing import List, Dict
from app.config.credentials_config import config


# Resend API key
resend.api_key = config.RESEND_API_KEY

VERIFICATION_EMAIL_TEMPLATE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Verify Your iShout Account</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f2ff;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">

  <!-- Hidden preheader -->
  <span style="display:none;font-size:1px;color:#f4f2ff;max-height:0;max-width:0;opacity:0;overflow:hidden;">
    One step left — verify your email to start using iShout.
  </span>

  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color:#f4f2ff;padding:48px 16px;">
    <tr>
      <td align="center">

        <!-- ── TOP LOGO ABOVE CARD ── -->
        <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin-bottom:28px;">
          <tr>
            <td style="text-align:center;">
              <span style="font-size:26px;font-weight:900;letter-spacing:4px;color:#170f49;text-transform:uppercase;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
                i<span style="color:#ff4e7e;">S</span>HOUT
              </span>
            </td>
          </tr>
        </table>

        <!-- ── CARD ── -->
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0"
               style="max-width:520px;background-color:#ffffff;border-radius:24px;overflow:hidden;">

          <!-- Pink gradient top bar -->
          <tr>
            <td style="height:5px;background:linear-gradient(90deg,#ff4e7e 0%,#ff9eb5 100%);font-size:0;line-height:0;">&nbsp;</td>
          </tr>

          <!-- Header: logo + hero icon -->
          <tr>
            <td style="padding:44px 48px 0;text-align:center;">

              <!-- Circular icon -->
              <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin:0 auto 32px;">
                <tr>
                  <td style="width:88px;height:88px;background:linear-gradient(145deg,#fff0f5,#ffe4ee);border-radius:50%;text-align:center;vertical-align:middle;">
                    <span style="font-size:36px;line-height:88px;display:block;">✉️</span>
                  </td>
                </tr>
              </table>

              <h1 style="margin:0 0 12px;font-size:25px;font-weight:800;color:#170f49;letter-spacing:-0.4px;line-height:1.25;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
                Verify your email address
              </h1>
              <p style="margin:0;font-size:15px;line-height:1.8;color:#8885a8;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
                Hi&nbsp;<strong style="color:#170f49;font-weight:700;">{company_name}</strong>&nbsp;👋<br/>
                Thanks for joining iShout! Tap the button below<br/>to confirm your email and activate your account.
              </p>

            </td>
          </tr>

          <!-- CTA -->
          <tr>
            <td style="padding:36px 48px 32px;text-align:center;">
              <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin:0 auto;">
                <tr>
                  <td style="border-radius:14px;background-color:#ff4e7e;">
                    <a href="{verification_link}"
                       style="display:inline-block;padding:18px 56px;font-size:15px;font-weight:700;color:#ffffff;text-decoration:none;letter-spacing:0.2px;border-radius:14px;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
                      Verify My Account &nbsp;&rarr;
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Expiry pill -->
          <tr>
            <td style="padding:0 48px 36px;text-align:center;">
              <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin:0 auto;">
                <tr>
                  <td style="background:#f7f5ff;border-radius:50px;padding:10px 22px;border:1px solid #ede9ff;">
                    <span style="font-size:13px;color:#8885a8;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
                      ⏳&nbsp;&nbsp;This link expires in&nbsp;<strong style="color:#170f49;">24 hours</strong>
                    </span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Hairline divider -->
          <tr>
            <td style="padding:0 48px;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                <tr><td style="height:1px;background:#f2efff;font-size:0;line-height:0;">&nbsp;</td></tr>
              </table>
            </td>
          </tr>

          <!-- Ignore note -->
          <tr>
            <td style="padding:0 48px 36px;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                <tr>
                  <td style="background:#fafbff;border-radius:12px;padding:16px 20px;border:1px solid #edeaff;">
                    <p style="margin:0;font-size:13px;color:#b3b0cc;line-height:1.7;text-align:center;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
                      Didn't create an iShout account?<br/>
                      <span style="color:#c9c7de;">You can safely ignore this email — no action needed.</span>
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Card footer (dark) -->
          <tr>
            <td style="background:#170f49;padding:22px 48px;text-align:center;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                <tr>
                  <td style="text-align:left;vertical-align:middle;">
                    <span style="font-size:14px;font-weight:900;letter-spacing:3px;color:#ffffff;text-transform:uppercase;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
                      iShout
                    </span>
                  </td>
                  <td style="text-align:right;vertical-align:middle;">
                    <span style="font-size:12px;color:rgba(255,255,255,0.4);font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
                      © 2025 &nbsp;·&nbsp;
                      <a href="https://app.ishout.ae" style="color:#ff4e7e;text-decoration:none;">app.ishout.ae</a>
                    </span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

        </table>
        <!-- /Card -->

        <!-- Below card -->
        <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin-top:22px;">
          <tr>
            <td style="text-align:center;">
              <p style="margin:0;font-size:12px;color:#b0aed0;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
                You received this email because you created an account at iShout.
              </p>
            </td>
          </tr>
        </table>

      </td>
    </tr>
  </table>

</body>
</html>
"""


async def send_verification_email(
    to: List[str],
    subject: str,
    company_name: str,
    token: str,
) -> Dict:

    verification_link = f"{config.FRONTEND_URL}/auth/verify-email?token={token}"

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
