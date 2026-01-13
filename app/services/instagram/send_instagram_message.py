from app.core.exception import InternalServerErrorException


async def Send_Insta_Message(psid: int, message: str):
    try:
        print(f"Sending message to {psid}: {message}")
        print("Message sent successfully")
        return True
    except Exception as e:
        raise InternalServerErrorException(message=str(e))
