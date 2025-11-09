from typing import List
from app.tools.instagram_influencers import search_instagram_influencers
from app.tools.tiktok_influencers import search_tiktok_influencers
from app.tools.youtube_influencers import search_youtube_influencers
import asyncio
import logging


async def search_influencers(
    platforms: List[str],
    category: List[str],
    followers: List[str],
    country: List[str],
    limit: int,
):
    try:
        logging.info(f"🔍 Platforms: {platforms}")
        tasks = []
        logging.info(f"🔍 Tasks: {tasks}")
        if "instagram" in platforms:
            tasks.append(
                search_instagram_influencers(
                    category=category,
                    limit=limit,
                    followers=followers,
                    country=country,
                )
            )
            logging.info(f"🔍 Instagram task: {tasks}")
        if "tiktok" in platforms:
            tasks.append(
                search_tiktok_influencers(
                    category=category,
                    limit=limit,
                    followers=followers,
                    country=country,
                )
            )
            logging.info(f"🔍 Tiktok task: {tasks}")
        if "youtube" in platforms:
            tasks.append(
                search_youtube_influencers(
                    category=category,
                    limit=limit,
                    followers=followers,
                    country=country,
                )
            )

        # ✅ Run all platform searches in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # ✅ Merge and handle exceptions
        combined_results = []
        for result in results:
            if isinstance(result, Exception):
                print(f"Platform error: {result}")
                continue
            combined_results.extend(result)

        return combined_results

    except Exception as e:
        raise ValueError(f"Error searching influencers: {str(e)}")
