import json
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse


async def webhook(request: Request):
    if request.method == "POST":
        try:
            body = await request.json()
        except Exception:
            body = None
        print(json.dumps(body, indent=4) if body is not None else "<no json body>")
        return JSONResponse(status_code=200, content={"message": "Webhook received"})

    if request.method == "GET":
        hub_mode = request.query_params.get("hub.mode")
        hub_challenge = request.query_params.get("hub.challenge")
        hub_verify_token = request.query_params.get("hub.verify_token")
        if hub_challenge:
            return PlainTextResponse(content=hub_challenge)
        else:
            return JSONResponse(
                status_code=200, content={"message": "Get web hook request"}
            )
