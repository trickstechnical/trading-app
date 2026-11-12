import logging
from apscheduler.schedulers.background import BackgroundScheduler

from app.paper_trading.monitor import monitor_positions

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone="Asia/Kolkata")


def _run_scheduled_monitor(app=None):
    if app is not None:
        with app.app_context():
            try:
                results = monitor_positions()
                if results:
                    logger.info("Scheduler executed monitor_positions: %d exit(s)", len(results))
            except Exception as e:
                logger.error("Error in scheduled monitor_positions: %s", e)
    else:
        monitor_positions()


def start_scheduler(app=None):
    if scheduler.running:
        return

    scheduler.add_job(
        func=_run_scheduled_monitor,
        args=[app],
        trigger="interval",
        minutes=5,
        id="paper_position_monitor",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    scheduler.start()
