from flask import Blueprint, jsonify

paper_bp = Blueprint("paper", __name__)


@paper_bp.get("/account")
def paper_account():
    # Replace with account data loaded from PostgreSQL.
    return jsonify({
        "mode": "paper",
        "starting_cash": 100_000,
        "cash": 100_000,
        "realised_pnl": 0,
        "open_position": None,
    })