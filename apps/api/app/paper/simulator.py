from dataclasses import dataclass, field

from app.paper.risk import validate_buy


@dataclass
class Position:
    quantity: int
    entry_price: float


@dataclass
class PaperAccount:
    cash: float = 100_000
    position: Position | None = None
    realised_pnl: float = 0.0
    orders: list[dict] = field(default_factory=list)


class PaperSimulator:
    def __init__(
        self,
        account: PaperAccount | None = None,
        slippage_bps: float = 5,
        fee_rate: float = 0.0003,
    ):
        self.account = account or PaperAccount()
        self.slippage_bps = slippage_bps
        self.fee_rate = fee_rate

    def _fill_price(self, market_price: float, side: str) -> float:
        if market_price <= 0:
            raise ValueError("Market price must be positive.")

        slippage = self.slippage_bps / 10_000

        if side == "BUY":
            return market_price * (1 + slippage)

        return market_price * (1 - slippage)

    def buy(self, market_price: float, quantity: int) -> dict:
        account = self.account

        if account.position is not None:
            raise ValueError("Only one open position is allowed in this MVP.")

        fill = self._fill_price(market_price, "BUY")
        notional = fill * quantity
        fees = notional * self.fee_rate

        validate_buy(
            cash=account.cash,
            price=fill,
            quantity=quantity,
        )

        if notional + fees > account.cash:
            raise ValueError("Insufficient cash after estimated fees.")

        account.cash -= notional + fees
        account.position = Position(quantity, fill)

        order = {
            "side": "BUY",
            "quantity": quantity,
            "fill_price": fill,
            "fees": fees,
            "status": "FILLED",
        }
        account.orders.append(order)
        return order

    def sell(self, market_price: float) -> dict:
        account = self.account
        position = account.position

        if position is None:
            raise ValueError("No open position to sell.")

        fill = self._fill_price(market_price, "SELL")
        proceeds = fill * position.quantity
        fees = proceeds * self.fee_rate

        entry_cost = position.entry_price * position.quantity
        entry_fees = entry_cost * self.fee_rate

        pnl = proceeds - fees - entry_cost - entry_fees
        account.cash += proceeds - fees
        account.realised_pnl += pnl
        account.position = None

        order = {
            "side": "SELL",
            "quantity": position.quantity,
            "fill_price": fill,
            "fees": fees,
            "realised_pnl": pnl,
            "status": "FILLED",
        }
        account.orders.append(order)
        return order

    def equity(self, market_price: float) -> float:
        account = self.account
        position_value = (
            account.position.quantity * market_price
            if account.position else 0.0
        )
        return account.cash + position_value