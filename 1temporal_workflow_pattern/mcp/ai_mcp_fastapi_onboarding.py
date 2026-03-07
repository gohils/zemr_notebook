# ---------------------------------------
# fastapi_ai_onboarding.py
# ---------------------------------------
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from temporalio.client import Client

app = FastAPI(title="AI-Powered Onboarding API")

# -------------------------------
# Environment-driven Temporal server
# -------------------------------
TEMPORAL_SERVER = os.getenv("TEMPORAL_SERVER", "localhost:7233")
TASK_QUEUE = os.getenv("TASK_QUEUE", "ai-onboarding-demo-task-queue")

# -------------------------------
# Pydantic model for input validation
# -------------------------------
class CustomerData(BaseModel):
    customer_id: str
    name: str
    email: str
    phone: str
    driver_license_image: str
    passport_image: str
    utility_bill_image: str

# -------------------------------
# FastAPI endpoint to start workflow
# -------------------------------
@app.post("/start_ai_onboarding/")
async def start_ai_onboarding(customer_data: CustomerData):
    """
    Starts the AI-powered customer onboarding workflow.

    Example payload:
    {
        "customer_id": "123e4567-e89b-12d3-a456-426614174000",
        "name": "John Doe",
        "email": "john.doe@gmail.com",
        "phone": "1234567890",
        "driver_license_image": "base64-or-url-of-driver-license.jpg",
        "passport_image": "base64-or-url-of-passport.jpg",
        "utility_bill_image": "base64-or-url-of-utility-bill.jpg"
    }
    """
    try:
        # Connect to Temporal server
        client = await Client.connect(TEMPORAL_SERVER)

        # Execute AI onboarding workflow
        result = await client.execute_workflow(
            workflow="CustomerOnboardingAIWorkflowMCP",
            args=[customer_data.dict()],
            id=f"onboarding-{customer_data.customer_id}",
            task_queue=TASK_QUEUE
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