MEDIA_TYPES = ("image", "video", "audio", "document", "sticker")


def parse_whatsapp_message(event: dict):
    entry = event.get("entry", [])
    if not entry:
        return None

    changes = entry[0].get("changes", [])
    if not changes:
        return None

    value = changes[0].get("value", {})
    messages = value.get("messages")
    if not messages:
        return None

    msg = messages[0]
    msg_type = msg.get("type", "text")

    # Extract text
    text = msg.get("text", {}).get("body", "")

    # Extract media fields when the message carries a media payload
    meta_media_id = None
    media_mime_type = None
    media_filename = None
    media_caption = None

    if msg_type in MEDIA_TYPES:
        media_block = msg.get(msg_type, {})
        meta_media_id = media_block.get("id")
        media_mime_type = media_block.get("mime_type")
        media_filename = media_block.get("filename")          # only for documents
        media_caption = media_block.get("caption", "")       # image/video captions
        # Use caption as the text body so it's not empty
        if not text and media_caption:
            text = media_caption

    return {
        "thread_id": msg.get("from"),
        "type": msg_type,
        "text": text,
        "interactive": msg.get("interactive"),
        "profile_name": value.get("contacts", [{}])[0]
        .get("profile", {})
        .get("name", "iShout"),
        "raw": value,
        # media fields (None for plain text messages)
        "meta_media_id": meta_media_id,
        "media_mime_type": media_mime_type,
        "media_filename": media_filename,
    }

