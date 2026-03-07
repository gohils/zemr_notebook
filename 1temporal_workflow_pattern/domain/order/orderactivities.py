import asyncio
import random
from temporalio import activity
from domain.order.ordermodels import OrderProcessingState


@activity.defn
async def read_order(
    state: OrderProcessingState,
) -> OrderProcessingState:
    """Load order details from order database."""

    print("📥 [DB READ] Fetching order from database...")

    await asyncio.sleep(0.5)

    print(f"   ✔ Order {state.order_id} loaded")

    return state


@activity.defn
async def validate_inventory(
    state: OrderProcessingState,
) -> OrderProcessingState:
    """Validate item availability in inventory system."""

    print("📦 [SERVICE CALL] Checking inventory availability...")

    await asyncio.sleep(1)

    state.inventory_ok = random.choice([True, True, True, False])

    print(f"   ✔ Inventory validation result: {state.inventory_ok}")

    return state


@activity.defn
async def fraud_check(
    state: OrderProcessingState,
) -> OrderProcessingState:
    """Run fraud detection analysis via fraud engine."""

    print("🛡 [HTTP POST] Sending transaction to fraud engine...")

    await asyncio.sleep(1)

    state.fraud_ok = random.choice([True, True, True, False])

    print(f"   ✔ Fraud check result: {state.fraud_ok}")

    return state


@activity.defn
async def charge_payment(
    state: OrderProcessingState,
) -> OrderProcessingState:
    """Charge customer payment via payment gateway."""

    print("💳 [PAYMENT API] Charging customer payment method...")

    await asyncio.sleep(1)

    print(f"   ✔ Payment successful for order {state.order_id}")

    return state


@activity.defn
async def update_order_status(
    state: OrderProcessingState,
) -> OrderProcessingState:
    """Persist order status update to database."""

    print(f"📝 [DB UPDATE] Updating order status to {state.status}...")

    await asyncio.sleep(0.5)

    print(f"   ✔ Order {state.order_id} status updated")

    return state


@activity.defn
async def order_publish_event(
    state: OrderProcessingState,
) -> OrderProcessingState:
    """Publish ORDER_COMPLETED or ORDER_REJECTED event."""

    print(f"📢 [EVENT] Publishing {state.status} event...")

    await asyncio.sleep(0.3)

    print(f"   ✔ Event published for order {state.order_id}")

    return state