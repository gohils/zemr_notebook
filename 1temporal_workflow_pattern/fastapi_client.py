from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import os
import asyncio
from temporalio.client import Client

TEMPORAL_SERVER = os.getenv("TEMPORAL_SERVER", "localhost:7233")
TASK_QUEUE = os.getenv("TEMPORAL_TASK_QUEUE", "demo-task-queue")

app = FastAPI(title="Temporal Workflow API")


# =======================
# Pydantic Payload Models
# =======================
class CustomerOnboardingPayload(BaseModel):
    customer_id: str
    first_name: str
    last_name: str
    email: str


class OrderItem(BaseModel):
    sku: str
    qty: int


class OrderProcessingPayload(BaseModel):
    order_id: str
    customer_id: str
    payment_method: str
    items: List[OrderItem]


# =======================
# Generic Workflow Starter
# =======================
async def start_workflow(workflow_type: str, payload: Dict[str, Any], workflow_id: str = None):
    client = await Client.connect(TEMPORAL_SERVER)
    if not workflow_id:
        workflow_id = f"{workflow_type}-{payload.get('customer_id', payload.get('order_id', 'anon'))}"

    handle = await client.start_workflow(
        workflow_type,
        payload,
        id=workflow_id,
        task_queue=TASK_QUEUE,
    )
    print(f"[FastAPI] Started workflow {workflow_type} (id={workflow_id}, run_id={handle.run_id})")
    return handle


# =======================
# Endpoints
# =======================
@app.post("/onboard-customer")
async def onboard_customer(payload: CustomerOnboardingPayload):
    """
    Trigger CustomerOnboardingWorkflow
    Example payload: \n
    {
        "customer_id": "CUST1001",
        "first_name": "Alice",
        "last_name": "Johnson",
        "email": "alice@example.com"
    }
    """
    handle = await start_workflow("CustomerOnboardingWorkflow", payload.dict())

    # Auto-simulate manual approval after 2 seconds (for demo)
    async def auto_approve():
        await asyncio.sleep(2)
        print("✋ Sending auto manual approval signal...")
        await handle.signal("manual_approval")

    asyncio.create_task(auto_approve())

    result = await handle.result()
    return {"workflow_id": handle.id, "run_id": handle.run_id, "result": result}


@app.post("/process-order")
async def process_order(payload: OrderProcessingPayload):
    """
    Trigger OrderProcessingWorkflow
    Example payload:  \n
    {
        "order_id": "ORD5001",
        "customer_id": "CUST1001",
        "payment_method": "credit_card",
        "items": [
            {"sku": "SKU001", "qty": 2},
            {"sku": "SKU002", "qty": 1}
        ]
    }
    """
    handle = await start_workflow("OrderProcessingWorkflow", payload.dict())
    result = await handle.result()
    return {"workflow_id": handle.id, "run_id": handle.run_id, "result": result}

# -------------------------------
# Run FastAPI standalone
# -------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)