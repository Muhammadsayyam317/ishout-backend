import json
import time
from typing import Optional, Dict
import httpx
from fastapi import (
    BackgroundTasks,
    Request,
    Response,
    WebSocket,
    WebSocketDisconnect,
    HTTPException,
    status,
)
from fastapi.responses import JSONResponse
from app.services.websocket_manager import ws_manager
from app.config import config
from app.core.auth import verify_token


PROFILE_CACHE: Dict[str, Dict] = {}
PROFILE_TTL_SEC = 3600
PROCESSED_MESSAGES: set = set()
MESSAGE_CACHE_TTL_SEC = 3600


async def _get_ig_username(
    psid: Optional[str], page_id: Optional[str] = None
) -> Optional[str]:
    if not psid or not config.PAGE_ACCESS_TOKEN:
        return None

    now = time.time()
    cached = PROFILE_CACHE.get(psid)
    if cached and now - cached.get("ts", 0) < PROFILE_TTL_SEC:
        return cached.get("username") or cached.get("name")

    async with httpx.AsyncClient(timeout=10.0) as client:

        if page_id:
            try:
                conversations_url = f"https://graph.facebook.com/{config.IG_GRAPH_API_VERSION}/{page_id}/conversations"
                conv_params = {
                    "fields": "participants{id,name,username}",
                    "access_token": config.PAGE_ACCESS_TOKEN,
                    "limit": 25,
                }

                conv_resp = await client.get(conversations_url, params=conv_params)
                if conv_resp.status_code == 200:
                    conv_data = conv_resp.json()
                    conversations = conv_data.get("data", [])
                    for conv in conversations:
                        participants = conv.get("participants", {})

                        if isinstance(participants, dict):
                            participants_list = participants.get("data", [])
                        elif isinstance(participants, list):
                            participants_list = participants
                        else:
                            continue

                        for participant in participants_list:
                            participant_id = participant.get("id")
                            if participant_id == psid:
                                username = participant.get(
                                    "username"
                                ) or participant.get("name")
                                if username:
                                    PROFILE_CACHE[psid] = {
                                        "username": participant.get("username"),
                                        "name": participant.get("name"),
                                        "ts": now,
                                    }
                                    print(
                                        f"👤 Fetched username via Conversations API: {username}"
                                    )
                                    return username

                    paging = conv_data.get("paging", {}).get("next")
                    if paging:
                        next_resp = await client.get(paging)
                        if next_resp.status_code == 200:
                            next_data = next_resp.json()
                            for conv in next_data.get("data", []):
                                participants = conv.get("participants", {})
                                if isinstance(participants, dict):
                                    participants_list = participants.get("data", [])
                                elif isinstance(participants, list):
                                    participants_list = participants
                                else:
                                    continue

                                for participant in participants_list:
                                    if participant.get("id") == psid:
                                        username = participant.get(
                                            "username"
                                        ) or participant.get("name")
                                        if username:
                                            PROFILE_CACHE[psid] = {
                                                "username": participant.get("username"),
                                                "name": participant.get("name"),
                                                "ts": now,
                                            }
                                            print(
                                                f"👤 Fetched username via Conversations API (page 2): {username}"
                                            )
                                            return username
                elif conv_resp.status_code == 403:
                    error_data = (
                        conv_resp.json()
                        if conv_resp.headers.get("content-type", "").startswith(
                            "application/json"
                        )
                        else {}
                    )

            except Exception as e:
                print(f" Conversations API failed for PSID {psid}: {str(e)}")

        graph_url = f"https://graph.facebook.com/{config.IG_GRAPH_API_VERSION}/{psid}"
        params = {
            "fields": "name,username,profile_pic,follower_count,is_user_follow_business,is_business_follow_user",
            "access_token": config.PAGE_ACCESS_TOKEN,
        }

        try:
            resp = await client.get(graph_url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                username = data.get("username") or data.get("name")
                if username:
                    PROFILE_CACHE[psid] = {
                        "username": data.get("username"),
                        "name": data.get("name"),
                        "profile_pic": data.get("profile_pic"),
                        "follower_count": data.get("follower_count"),
                        "ts": now,
                    }
                    print(f"Successfully fetched username for PSID {psid}: {username}")
                    return username
            elif resp.status_code == 403:
                pass
            else:
                error_data = (
                    resp.json()
                    if resp.headers.get("content-type", "").startswith(
                        "application/json"
                    )
                    else {}
                )
                print(f" Failed to fetch username for PSID {psid}: {resp.status_code}")
                print(
                    f"   Error: {error_data.get('error', {}).get('message', 'Unknown error')}"
                )
        except Exception as e:
            print(f" Error fetching username for PSID {psid}: {str(e)}")

    return None


async def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == config.META_VERIFY_TOKEN:
        return Response(content=challenge, status_code=200)
    return Response(status_code=403)


async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        body = await request.json()
    except json.JSONDecodeError:
        print(" Invalid JSON received")
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    print("📩 Incoming Webhook Body:", json.dumps(body, indent=2))
    current_time = time.time()
    if hasattr(handle_webhook, "_last_cleanup"):
        if current_time - handle_webhook._last_cleanup > 3600:
            PROCESSED_MESSAGES.clear()
            handle_webhook._last_cleanup = current_time
    else:
        handle_webhook._last_cleanup = current_time

    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})

            if "message" in value:
                message_id = value["message"].get("mid")
                if message_id and message_id in PROCESSED_MESSAGES:
                    print(f"Skipping duplicate message: {message_id}")
                    continue

                if message_id:
                    PROCESSED_MESSAGES.add(message_id)

                psid = value.get("from", {}).get("id")
                message_data = value["message"]
                text = message_data.get("text", "")
                attachments = message_data.get("attachments", [])

                # Process attachments
                attachment_list = []
                for attachment in attachments:
                    attachment_list.append(
                        {
                            "type": attachment.get("type"),
                            "url": attachment.get("payload", {}).get("url"),
                        }
                    )

                # Only process if there's text or attachments
                if text or attachments:
                    username = await _get_ig_username(
                        psid, value.get("to", {}).get("id")
                    )
                    display_name = username or f"User_{psid[:6]}"
                    print("=========== IG MESSAGE RECEIVED (Direct) ===========")
                    print(f" Username: {display_name}")
                    print(f" PSID: {psid}")
                    print(f" Message: {text}")
                    if attachments:
                        print(
                            f" Attachments: {len(attachments)} ({', '.join([a.get('type', 'unknown') for a in attachments])})"
                        )
                    print("===========================================")

                    broadcast_data = {
                        "type": "ig_reply",
                        "from_psid": psid,
                        "to_page_id": value.get("to", {}).get("id"),
                        "from_username": display_name,
                        "text": text,
                        "timestamp": value.get("timestamp", time.time()),
                    }

                    if attachments:
                        broadcast_data["attachments"] = attachment_list

                    background_tasks.add_task(
                        ws_manager.broadcast,
                        broadcast_data,
                    )

        # Handle Facebook Messenger/Instagram format: entry[].messaging[]
        # for messaging_event in entry.get("messaging", []):
        #     message = messaging_event.get("message")
        #     # Process if message has text or attachments
        #     if message and (message.get("text") or message.get("attachments")):
        #         message_id = message.get("mid")
        #         if message_id and message_id in PROCESSED_MESSAGES:
        #             print(f"Skipping duplicate message: {message_id}")
        #             continue

        #         if message_id:
        #             PROCESSED_MESSAGES.add(message_id)

        #         sender = messaging_event.get("sender", {})
        #         recipient = messaging_event.get("recipient", {})
        #         psid = sender.get("id")
        #         page_id = recipient.get("id")
        #         text = message.get("text", "")
        #         attachments = message.get("attachments", [])
        #         timestamp = messaging_event.get("timestamp", time.time())

        #         # Process attachments
        #         attachment_list = []
        #         for attachment in attachments:
        #             attachment_list.append(
        #                 {
        #                     "type": attachment.get("type"),
        #                     "url": attachment.get("payload", {}).get("url"),
        #                 }
        #             )

        #         username = await _get_ig_username(psid, page_id)
        #         display_name = username or f"User_{psid[:8]}"

        #         if attachments:
        #             print(
        #                 f" Attachments: {len(attachments)} ({', '.join([a.get('type', 'unknown') for a in attachments])})"
        #             )
        #         print("===========================================")

        #         broadcast_data = {
        #             "type": "ig_reply",
        #             "from_psid": psid,
        #             "to_page_id": page_id,
        #             "from_username": display_name,
        #             "text": text,
        #             "timestamp": timestamp,
        #         }

        #         if attachments:
        #             broadcast_data["attachments"] = attachment_list

        #         background_tasks.add_task(
        #             ws_manager.broadcast,
        #             broadcast_data,
        #         )

    return JSONResponse({"status": "received"})


async def websocket_notifications(websocket: WebSocket):
    token = websocket.query_params.get("token")

    if not token:
        await websocket.accept()
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION, reason="Missing token"
        )
        return
    user_id = None
    role = None
    try:
        payload = verify_token(token)
        user_id = payload.get("user_id")
        role = payload.get("role")
        if role != "admin":
            await websocket.accept()
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION, reason="Admin access required"
            )
            return
    except HTTPException as e:
        await websocket.accept()
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=e.detail)
        return
    except Exception:
        await websocket.accept()
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token"
        )
        return

    await ws_manager.connect(websocket, user_id=user_id, role=role)
    try:
        while True:
            data = await websocket.receive_json()
            if isinstance(data, dict) and data.get("action") == "stats":
                await websocket.send_json(
                    {"type": "stats", **(await ws_manager.stats())}
                )
            else:
                await websocket.send_json({"type": "noop"})
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, user_id=user_id, role=role)
    except Exception:
        await ws_manager.disconnect(websocket, user_id=user_id, role=role)
        try:
            await websocket.close(code=1011)
        except Exception:
            pass
