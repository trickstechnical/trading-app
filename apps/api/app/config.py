import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PAPER_STARTING_CASH = float(
        os.getenv("PAPER_STARTING_CASH", "100000")
    )

    PAPER_TRADING_ENABLED = (
        os.getenv("PAPER_TRADING_ENABLED", "true").lower() == "true"
    )

    # This MVP must never place live orders.
    LIVE_TRADING_ENABLED = False

    START_PAPER_SCHEDULER = True