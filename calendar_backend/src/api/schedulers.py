"""Background scheduling endpoints (stub), and APScheduler integration for periodic jobs (reminders, email sync)."""

from fastapi import APIRouter
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

router = APIRouter(prefix="/schedulers", tags=["schedulers"])

_scheduler: BackgroundScheduler = None

def send_due_reminders():
    # This stub job would query due reminders & use Resend to notify
    logging.info("Background: send_due_reminders called (stub)")

def sync_gmail_emails():
    # This stub job would fetch fresh emails from Gmail for connected users
    logging.info("Background: sync_gmail_emails called (stub)")

def setup_scheduler():
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        return
    _scheduler = BackgroundScheduler()
    # Every 5 minutes, check for reminders to send
    _scheduler.add_job(send_due_reminders, IntervalTrigger(minutes=5), id="send_reminders")
    # Every 10 minutes, sync Gmail
    _scheduler.add_job(sync_gmail_emails, IntervalTrigger(minutes=10), id="sync_gmail")
    _scheduler.start()
    logging.info("APScheduler started (background reminder/email jobs)")

# Run at import/server startup
try:
    setup_scheduler()
except Exception as e:
    logging.error(f"Failed to initialize scheduler: {e}")

# PUBLIC_INTERFACE
@router.get("/")
def scheduling_root():
    """
    Show scheduler status and running jobs.
    """
    jobs = []
    if _scheduler:
        jobs = [f"{j.id}: {j.next_run_time}" for j in _scheduler.get_jobs()]
    return {"scheduler": "apscheduler", "jobs": jobs}
