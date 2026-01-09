import httpx
from app.config.credentials_config import config


url = f"https://graph.facebook.com/v23.0/{config.IG_BUSINESS_ID}/media?fields=id,caption,media_type,permalink,timestamp&access_token={config.INSTAGRAM_PAGE_ACCESS_TOKEN}"

response = httpx.AsyncClient().get(url)
data = response.json()
