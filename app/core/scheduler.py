from apscheduler.job import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from pymongo import MongoClient


from app.config import config
from app.agents.Instagram.nodes.track_response_node import track_unresponsive_users


jobstores = {
    "default": MongoDBJobStore(
        client=MongoClient(config.MONGODB_ATLAS_URI),
        database="scheduler",
        collection="jobs",
    )
}

scheduler = BackgroundScheduler(
    jobstores=jobstores,
    timezone=timezone.utc,
)


def start_scheduler():
    if not scheduler.running:
        scheduler.start()

    scheduler.add_job(
        track_unresponsive_users,
        trigger="cron",
        hour=12,
        minute=0,
        id="track_unresponsive_users",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )


def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
