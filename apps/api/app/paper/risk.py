def validate_buy(
    cash: float,
    price: float,
    quantity: int,
    max_order_value: float = 20_000,
) -> None:
    if price <= 0:
        raise ValueError("Price must be positive.")

    if quantity <= 0:
        raise ValueError("Quantity must be positive.")

    order_value = price * quantity

    if order_value > max_order_value:
        raise ValueError("Order exceeds the paper order-value limit.")

    if order_value > cash:
        raise ValueError("Insufficient virtual cash.")