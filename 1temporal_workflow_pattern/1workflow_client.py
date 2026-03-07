import asyncio
from temporalio.client import Client
from pydantic import BaseModel, EmailStr
from typing import Optional  # <-- needed for Optional[str]

class CustomerOnboardingRequest(BaseModel):
    """Input payload for starting customer onboarding workflow."""
    name: str
    email: EmailStr
    city: str
    phone: str
    age: int
    occupation: Optional[str] = None


TEMPORAL_SERVER = "localhost:7233"
TASK_QUEUE = "customer-task-queue"


async def start_workflow(workflow_type: str, payload: CustomerOnboardingRequest, workflow_id: str = None):
    """
    Start a workflow using its type name (string) instead of workflow class reference.
    Payload can be a Pydantic model.
    """
    client = await Client.connect(TEMPORAL_SERVER)

    # Generate workflow_id if not provided
    if not workflow_id:
        workflow_id = f"{workflow_type}-{payload.name.replace(' ', '-')}-001"

    print(f"\n🎯 Starting workflow '{workflow_type}' with ID '{workflow_id}'...")

    # Execute workflow by type string; Pydantic model works as input
    handle = await client.start_workflow(
        workflow_type,
        payload,  # Pydantic model works as input
        id=workflow_id,
        task_queue=TASK_QUEUE,
    )

    print(f"[Client] Workflow '{workflow_type}' started (run_id={handle.run_id})")

    result = await handle.result()
    print(f"[Client] Workflow '{workflow_type}' completed with result:\n{result}\n")

    return result


async def main():
    # Prepare Pydantic input
    input_data = CustomerOnboardingRequest(
        name="Sid G",
        email="sid@example.com",
        city="Melbourne",
        phone="+61412345678",
        age=35,
        occupation="Engineer"
    )

    # Start workflow using type string
    await start_workflow("CustomerOnboardingWorkflow", input_data)

async def main_multi():
    test_payloads = [
        CustomerOnboardingRequest(name="Alice Happy", email="alice@example.com", city="Melbourne", phone="+61411111111", age=28, occupation="Engineer"),
        CustomerOnboardingRequest(name="Bob Risky", email="bob@example.com", city="Sydney", phone="+61422222222", age=40, occupation="Manager"),
        CustomerOnboardingRequest(name="Charlie LowCredit", email="charlie@example.com", city="Brisbane", phone="+61433333333", age=32, occupation="Teacher"),
    ]

    for payload in test_payloads:
        await start_workflow("CustomerOnboardingWorkflow", payload)

if __name__ == "__main__":
    asyncio.run(main_multi())