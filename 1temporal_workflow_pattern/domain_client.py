import asyncio
import os
from temporalio.client import Client

TEMPORAL_SERVER = os.getenv("TEMPORAL_SERVER", "localhost:7233")
TASK_QUEUE = os.getenv("TEMPORAL_TASK_QUEUE", "demo-task-queue")


async def start_workflow(workflow_type: str, payload: dict, workflow_id: str = None):
    """
    Start a workflow by workflow type name (no class import needed)
    """
    client = await Client.connect(TEMPORAL_SERVER)

    if not workflow_id:
        workflow_id = f"{workflow_type}-{payload.get('customer_id', payload.get('order_id', 'anon'))}"

    print(f"\n🎯 Starting workflow '{workflow_type}' with ID '{workflow_id}'...")

    handle = await client.start_workflow(
        workflow_type,  # just the string name
        payload,        # input payload (dict or Pydantic)
        id=workflow_id,
        task_queue=TASK_QUEUE,
    )

    print(f"[Client] Workflow '{workflow_type}' started (run_id={handle.run_id})")
    result = await handle.result()
    print(f"[Client] Workflow '{workflow_type}' completed with result: {result}\n")
    return result


async def main():
    # Customer Onboarding
    onboarding_payload = {
        "customer_id": "CUST1001",
        "first_name": "Alice",
        "last_name": "Johnson",
        "email": "alice@example.com"
    }
    await start_workflow("CustomerOnboardingWorkflow", onboarding_payload)

    # Order Processing
    order_payload = {
        "order_id": "ORD5001",
        "customer_id": "CUST1001",
        "payment_method": "credit_card",
        "items": [
            {"sku": "SKU001", "qty": 2},
            {"sku": "SKU002", "qty": 1},
        ]
    }
    await start_workflow("OrderProcessingWorkflow", order_payload)


if __name__ == "__main__":
    asyncio.run(main())