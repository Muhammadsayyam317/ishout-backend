from fastapi import Request
from app.agents.nodes.graph import whatsapp_agent


async def handle_whatsapp_events(request: Request):
    event = await request.json()
    event_data = event["entry"][0]["changes"][0]["value"]
    state = {"event_data": event_data}
    thread_id = event_data["messages"][0]["from"]
    await whatsapp_agent.ainvoke(
        state, config={"configurable": {"thread_id": thread_id}}
    )
    return {"status": "ok"}
