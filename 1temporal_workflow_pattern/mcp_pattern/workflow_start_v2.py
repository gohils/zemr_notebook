# workflow_start_refactored.py
import asyncio
from workflow_mcp_v2 import CustomerOnboardingWorkflow, CustomerOnboardingInput
from temporalio.client import Client as TemporalClient

async def main():
    # -------------------------------
    # Connect to the local Temporal service
    # -------------------------------
    client = await TemporalClient.connect("localhost:7233")

    # -------------------------------
    # Prepare workflow input
    # -------------------------------
    input_data = CustomerOnboardingInput(
        customer_id="CUST-001p",
        email="alice@example.com",
        mcp_url="http://localhost:8080/mcp",
        welcome_message="Welcome Alice! Your account is ready."
    )

    # -------------------------------
    # Execute the workflow
    # -------------------------------
    # Workflow-local state will be returned as final_record
    final_record = await client.execute_workflow(
        CustomerOnboardingWorkflow.run,  # workflow run method reference
        input_data,                      # input data object
        id="customer-onboarding-001",    # unique workflow ID
        task_queue="onboarding-tq"       # task queue name
    )

    # -------------------------------
    # Print final workflow-local state
    # -------------------------------
    print("✅ Workflow completed. Final customer record:")
    print(final_record)


if __name__ == "__main__":
    asyncio.run(main())