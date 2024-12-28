# modules/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from process_recurring import process_recurring_transactions
import logging

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Schedule the job to run daily at midnight
    scheduler.add_job(process_recurring_transactions, 'cron', hour=0, minute=0)
    scheduler.start()
    logger.info("Scheduler started: Recurring transactions will be processed daily at midnight.")

    # Shutdown scheduler when exiting the app
    import atexit
    atexit.register(lambda: scheduler.shutdown())
