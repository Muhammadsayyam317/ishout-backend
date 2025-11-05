from fastapi.responses import JSONResponse


def get_privacy_policy():
    with open("privacy_policy.md", "r", encoding="utf-8") as file:
        return JSONResponse(status_code=200, content={"privacy_policy": file.read()})
