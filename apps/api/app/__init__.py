from flask import Flask, jsonify

from app.config import Config
from app.extensions import db, migrate
from app.market_data.ingestion import register_ingestion_command


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "mode": "paper"})

    # Import models so Flask-Migrate can discover them.
    from app import models  # noqa: F401

    from app.routes.paper_trading import paper_bp
    from app.routes.market import market_bp
    from app.routes.signals import signals_bp

    app.register_blueprint(market_bp, url_prefix="/api/market")
    app.register_blueprint(signals_bp, url_prefix="/api/signals")
    app.register_blueprint(paper_bp, url_prefix="/api/paper")

    from app.paper_trading.scheduler import start_scheduler

    if app.config.get("START_PAPER_SCHEDULER", False):
        start_scheduler(app)

    register_ingestion_command(app)

    @app.cli.command("init-paper-account")
    def init_paper_account():
        from app.models import PaperAccount

        account = PaperAccount.query.filter_by(id=1).first()

        if account:
            print("Paper account already exists.")
            return

        account = PaperAccount(
            id=1,
            name="Default Paper Account",
            initial_balance=100000,
            balance=100000,
        )

        db.session.add(account)
        db.session.commit()

        print("Paper account created with ₹1,00,000 virtual capital.")

    return app