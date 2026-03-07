from temporalio import workflow
from datetime import timedelta
import asyncio
import random

with workflow.unsafe.imports_passed_through():
    from domain.order.ordermodels import OrderProcessingInput, OrderProcessingState
    from domain.order.orderactivities import (
        read_order,
        validate_inventory,
        fraud_check,
        charge_payment,
        update_order_status,
        order_publish_event,
    )


@workflow.defn
class OrderProcessingWorkflow:
    """Workflow to process an order: validate, fraud check, payment, status update, and event publish."""

    def __init__(self):
        self.timeout = timedelta(seconds=30)

    async def execute(self, activity, state: OrderProcessingState):
        """Execute an activity with standard timeout."""
        return await workflow.execute_activity(
            activity,
            state,
            start_to_close_timeout=self.timeout,
        )

    @workflow.run
    async def run(self, payload: OrderProcessingInput) -> OrderProcessingState:
        """Run the order processing workflow end-to-end."""

        print(f"\n🚀 Starting workflow for Order: {payload.order_id}")
        state = OrderProcessingState(**payload.dict())

        # Step 1: Load order
        print("⏳ Step 1: Reading order from DB...")
        state = await self.execute(read_order, state)
        await asyncio.sleep(0.2)  # simulate workflow-level processing

        # Step 2: Parallel validation: inventory + fraud
        print("⏳ Step 2: Running parallel inventory & fraud checks...")
        inv, fraud = await asyncio.gather(
            workflow.execute_activity(validate_inventory, state, start_to_close_timeout=self.timeout),
            workflow.execute_activity(fraud_check, state, start_to_close_timeout=self.timeout),
        )
        state.inventory_ok = inv.inventory_ok
        state.fraud_ok = fraud.fraud_ok
        print(f"   ✔ Inventory OK: {state.inventory_ok}, Fraud OK: {state.fraud_ok}")

        # Step 3: Conditional rejection
        if not state.inventory_ok or not state.fraud_ok:
            state.status = "REJECTED"
            print(f"⚠ Order {state.order_id} rejected due to validation failure")
            state = await self.execute(update_order_status, state)
            await self.execute(order_publish_event, state)
            print(f"🚫 Workflow finished: Order {state.order_id} REJECTED")
            return state

        # Step 4: Payment
        print("⏳ Step 3: Charging payment...")
        state = await self.execute(charge_payment, state)
        await asyncio.sleep(0.2)
        state.status = "COMPLETED"
        print(f"   ✔ Payment processed for order {state.order_id}")

        # Step 5: Update DB status
        print("⏳ Step 4: Updating order status in DB...")
        state = await self.execute(update_order_status, state)

        # Step 6: Publish event
        print("⏳ Step 5: Publishing order event...")
        state = await self.execute(order_publish_event, state)

        print(f"✅ Workflow finished: Order {state.order_id} COMPLETED\n")
        return state