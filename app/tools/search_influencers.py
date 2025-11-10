from typing import List
from app.tools.instagram_influencers import search_instagram_influencers
from app.tools.tiktok_influencers import search_tiktok_influencers
from app.tools.youtube_influencers import search_youtube_influencers
import asyncio


async def search_influencers(
    platforms: List[str],
    category: List[str],
    followers: List[str],
    country: List[str],
    limit: int,
):
    try:
        tasks = []
        platforms_lower = [
            p.strip().lower() if isinstance(p, str) else str(p).strip().lower()
            for p in platforms
        ]

        if "instagram" in platforms_lower:
            tasks.append(
                search_instagram_influencers(
                    category=category,
                    limit=limit,
                    followers=followers,
                    country=country,
                )
            )
        if "tiktok" in platforms_lower:
            tasks.append(
                search_tiktok_influencers(
                    category=category,
                    limit=limit,
                    followers=followers,
                    country=country,
                )
            )
        if "youtube" in platforms_lower:
            tasks.append(
                search_youtube_influencers(
                    category=category,
                    limit=limit,
                    followers=followers,
                    country=country,
                )
            )
        results = await asyncio.gather(*tasks, return_exceptions=True)
        combined_results = []
        for result in results:
            if isinstance(result, Exception):
                print(f"Platform error: {result}")
                continue
            combined_results.extend(result)

        return combined_results

    except Exception as e:
        raise ValueError(f"Error searching influencers: {str(e)}")
