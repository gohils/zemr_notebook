import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from temporalio.client import Client

app = FastAPI(title="Temporal Workflow API")

# -------------------------------
# Environment-driven Temporal server
# -------------------------------
TEMPORAL_SERVER = os.getenv("TEMPORAL_SERVER", "localhost:7233")

# -------------------------------
# Pydantic model for input validation
# -------------------------------
class CustomerData(BaseModel):
    customer_id: str
    first_name: str
    last_name: str
    email: str

# -------------------------------
# FastAPI endpoint to start workflow
# -------------------------------
@app.post("/start_onboarding/")
async def start_onboarding(customer_data: CustomerData):
    try:
        # Connect to Temporal server
        client = await Client.connect(TEMPORAL_SERVER)

        # Execute workflow by workflow type name as string
        result = await client.execute_workflow(
            workflow="CustomerOnboardingWorkflow",
            args=[customer_data.dict()],
            id=f"onboarding-{customer_data.customer_id}",
            task_queue="customer-onboarding-queue"
        )

        return {"status": "success", "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------
# Run FastAPI with Uvicorn if standalone
# -------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)