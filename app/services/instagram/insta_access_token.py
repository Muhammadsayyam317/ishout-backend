import requests
from app.config.credentials_config import config


url = f"https://graph.facebook.com/v23.0/{config.IG_BUSINESS_ID}?fields=access_token&access_token={config.INSTAGRAM_PAGE_ACCESS_TOKEN}"

response = requests.get(url)
data = response.json()
print(data.get("access_token"))
