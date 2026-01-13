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

    return {
        "thread_id": msg.get("from"),
        "type": msg.get("type"),
        "text": msg.get("text", {}).get("body", ""),
        "interactive": msg.get("interactive"),
        "profile_name": value.get("contacts", [{}])[0]
        .get("profile", {})
        .get("name", "iShout"),
        "raw": value,
    }
