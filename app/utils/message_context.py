import io

import httpx
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer

from app.Schemas.instagram.message_schema import GenerateReplyOutput
from app.config.credentials_config import config
from app.utils.printcolors import Colors
from app.utils.prompts import (
    ANALYZE_INFLUENCER_WHATSAPP_PROMPT,
    NEGOTIATE_INFLUENCER_DM_PROMPT,
)


def build_message_context(last_messages: list[dict], latest: str) -> str:
    """
    Build conversation context for the AI reply.
    """

    history = "\n".join(
        f"{'AI' if msg.get('sender_type') == 'AI' else 'User'}: {msg.get('message', '')}"
        for msg in last_messages
    )

    return f"""
{NEGOTIATE_INFLUENCER_DM_PROMPT}

Conversation so far:
{history}

Latest message:
User: {latest}

Write the next reply as a natural human text message.
""".strip()


def build_whatsapp_message_context(last_messages: list[dict], latest: str) -> str:
    history = "\n".join(
        f"{'AI' if msg.get('sender_type') == 'AI' else 'User'}: {msg.get('message', '')}"
        for msg in last_messages
    )

    return f"""
{ANALYZE_INFLUENCER_WHATSAPP_PROMPT}

Conversation so far:
{history}

Latest message:
User: {latest}

Write the next reply as a natural WhatsApp message.
Keep it short, friendly, and human.
""".strip()


def normalize_ai_reply(reply) -> str:
    DEFAULT_REPLY = "Thanks for your message! Let me check and get back to you shortly."

    if isinstance(reply, GenerateReplyOutput):
        return reply.reply or DEFAULT_REPLY
    elif isinstance(reply, dict) and "reply" in reply:
        return reply["reply"] or DEFAULT_REPLY
    elif isinstance(reply, str):
        return reply or DEFAULT_REPLY
    else:
        return DEFAULT_REPLY


def get_history_list(state: dict) -> list:
    """
    Return state['history'] as a list. Never return a dict.
    Mongo or other storage may persist history in a shape that deserializes as a dict;
    passing that to agents or calling .append()/.extend() on it causes runtime errors.
    """
    h = state.get("history")
    if isinstance(h, list):
        return h
    return []


def set_history_list(state: dict, history: list) -> None:
    """Ensure state['history'] is a list so later setdefault/append are safe."""
    state["history"] = history if isinstance(history, list) else []


def history_to_agent_messages(history: list[dict]) -> list[dict]:
    """
    Convert our history (sender_type: 'USER'|'AI', message: str) to the format
    expected by the agents API: role 'user'|'assistant', content: str.
    """
    # IMPORTANT:
    # - We keep full history in Mongo/state for the frontend.
    # - For LLM context, we only send the most recent window.
    recent_history = history[-20:] if isinstance(history, list) else []

    out = []
    for msg in recent_history:
        if not isinstance(msg, dict):
            continue
        role = "user" if (msg.get("sender_type") or "").upper() == "USER" else "assistant"
        content = (msg.get("message") or msg.get("content") or "").strip()
        if content:
            out.append({"role": role, "content": content})
    return out


def build_campaign_brief_pdf_bytes(brief: dict) -> bytes | None:
    """
    Build a professional-looking campaign brief PDF from a brief dict.

    Excludes internal / non-brief fields like id and campaign_logo_url.
    Skips sections that are null or empty.
    """
    try:
        if not isinstance(brief, dict):
            return None

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        title = (brief.get("title") or "").strip()
        if title:
            story.append(Paragraph(title, styles["Title"]))
            story.append(Spacer(1, 12))

        # Helper to add a section with bullet list
        def add_section(heading: str, items):
            cleaned = [str(i).strip() for i in (items or []) if str(i).strip()]
            if not cleaned:
                return
            story.append(Paragraph(heading, styles["Heading2"]))
            story.append(Spacer(1, 4))
            bullets = [
                ListItem(Paragraph(text, styles["BodyText"]), bulletText="•")
                for text in cleaned
            ]
            story.append(ListFlowable(bullets, bulletType="bullet", leftIndent=16))
            story.append(Spacer(1, 10))

        # Map brief fields to nicely labelled sections
        add_section("Campaign Overview", brief.get("campaign_overview"))
        add_section("Campaign Objectives", brief.get("campaign_objectives"))
        add_section("Target Audience", brief.get("target_audience"))
        add_section("Influencer Profile", brief.get("influencer_profile"))
        add_section("Key Campaign Message", brief.get("key_campaign_message"))
        add_section("Content Direction", brief.get("content_direction"))
        add_section("Deliverables per Influencer", brief.get("deliverables_per_influencer"))
        add_section("Hashtags & Mentions", brief.get("hashtags_mentions"))
        add_section("Timeline", brief.get("timeline"))
        add_section("Approval Process", brief.get("approval_process"))
        add_section("KPIs & Success Metrics", brief.get("kpis_success_metrics"))
        add_section("Usage Rights", brief.get("usage_rights"))
        add_section("Do's & Don'ts", brief.get("dos_donts"))

        # Optional metadata sections (platform, category, followers, country)
        def add_simple_section(heading: str, value):
            if not value:
                return
            if isinstance(value, list):
                cleaned = [str(v).strip() for v in value if str(v).strip()]
                if not cleaned:
                    return
                text = ", ".join(cleaned)
            else:
                text = str(value).strip()
                if not text:
                    return
            story.append(Paragraph(heading, styles["Heading2"]))
            story.append(Spacer(1, 4))
            story.append(Paragraph(text, styles["BodyText"]))
            story.append(Spacer(1, 10))

        add_simple_section("Platform", brief.get("platform"))
        add_simple_section("Category", brief.get("category"))
        add_simple_section("Followers", brief.get("followers"))
        add_simple_section("Country", brief.get("country"))

        if not story:
            return None

        doc.build(story)
        buffer.seek(0)
        return buffer.read()
    except Exception as e:
        print(f"{Colors.RED}[build_campaign_brief_pdf_bytes] Failed to build PDF: {e}")
        return None


async def upload_media_to_meta(file_bytes: bytes, mime_type: str, filename: str) -> str | None:
    """
    Generic helper to upload media to Meta's WhatsApp Cloud API media endpoint.

    Returns media_id on success, or None on failure.
    """
    if not file_bytes:
        return None

    try:
        phone_number_id = "967002123161751"
        url = f"https://graph.facebook.com/v22.0/{phone_number_id}/media"
        headers = {
            "Authorization": f"Bearer {config.META_WHATSAPP_ACCESSSTOKEN}",
        }
        files = {"file": (filename, file_bytes, mime_type)}
        data = {
            "messaging_product": "whatsapp",
            "type": mime_type,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, data=data, files=files)

        response.raise_for_status()
        payload = response.json()
        media_id = payload.get("id")
        if not media_id:
            print(
                f"{Colors.RED}[upload_media_to_meta] No media id in response: {payload}"
            )
            return None
        return media_id
    except Exception as e:
        print(f"{Colors.RED}[upload_media_to_meta] Failed to upload media: {e}")
        return None
