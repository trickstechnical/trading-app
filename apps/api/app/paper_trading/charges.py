from decimal import Decimal, ROUND_HALF_UP


# FYERS standard NSE equity-delivery assumptions
BROKERAGE_CAP = Decimal("20")
BROKERAGE_RATE = Decimal("0.003")       # 0.3%
STT_RATE = Decimal("0.001")             # 0.1%
NSE_TRANSACTION_RATE = Decimal("0.000030699")  # 0.0030699%
SEBI_RATE = Decimal("0.000001")         # ₹10 per crore
STAMP_DUTY_RATE = Decimal("0.00015")    # 0.015%
IPFT_RATE = Decimal("0.000000001")      # ₹0.01 per crore
GST_RATE = Decimal("0.18")
DP_CHARGE = Decimal("12.50")


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_equity_delivery_charges(
    price: Decimal,
    quantity: int,
    side: str,
) -> dict:
    """
    Calculate estimated FYERS NSE equity-delivery charges.

    side: BUY or SELL
    """

    side = side.upper()

    if side not in {"BUY", "SELL"}:
        raise ValueError("side must be BUY or SELL")

    if price <= 0 or quantity <= 0:
        raise ValueError("price and quantity must be positive")

    turnover = price * quantity

    brokerage = min(
        BROKERAGE_CAP,
        turnover * BROKERAGE_RATE,
    )

    stt = turnover * STT_RATE

    exchange_charges = turnover * NSE_TRANSACTION_RATE
    sebi_charges = turnover * SEBI_RATE
    ipft_charges = turnover * IPFT_RATE

    stamp_duty = (
        turnover * STAMP_DUTY_RATE
        if side == "BUY"
        else Decimal("0")
    )

    dp_charges = (
        DP_CHARGE
        if side == "SELL"
        else Decimal("0")
    )

    gst = (
        brokerage
        + exchange_charges
        + sebi_charges
        + ipft_charges
        + dp_charges
    ) * GST_RATE

    total_charges = (
        brokerage
        + stt
        + exchange_charges
        + sebi_charges
        + ipft_charges
        + stamp_duty
        + dp_charges
        + gst
    )

    return {
        "turnover": money(turnover),
        "brokerage": money(brokerage),
        "stt": money(stt),
        "exchange_charges": money(exchange_charges),
        "sebi_charges": money(sebi_charges),
        "ipft_charges": money(ipft_charges),
        "stamp_duty": money(stamp_duty),
        "dp_charges": money(dp_charges),
        "gst": money(gst),
        "total_charges": money(total_charges),
    }