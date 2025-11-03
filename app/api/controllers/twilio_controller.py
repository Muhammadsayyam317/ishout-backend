from typing import Dict, Any
from twilio.rest import Client
from app.config import config

async def send_message(request_data: Dict[str, Any] = None):
    """
    Send a WhatsApp message using Twilio
    
    Args:
        request_data: Optional request data, not used in the current implementation
        
    Returns:
        str: The SID of the created message
    """
    # Get Twilio credentials from centralized config
    account_sid = config.TWILIO_ACCOUNT_SID
    auth_token = config.TWILIO_AUTH_TOKEN
    
    if not account_sid or not auth_token:
        raise ValueError("Twilio credentials not found in configuration")
    
    # Initialize Twilio client
    client = Client(account_sid, auth_token)
    
    try:
        # Create and send message
        message = client.messages.create(
            body="Hello, this is a test message",
            from_="whatsapp:+14155238886",
            to="whatsapp:+923240149841"
        )
        
        return message.sid
    except Exception as e:
        raise