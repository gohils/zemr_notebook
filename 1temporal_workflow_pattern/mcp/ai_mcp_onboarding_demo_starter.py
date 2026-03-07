# --------------------------------------------
# Starter Script: Test CustomerOnboardingAIWorkflowMCP
# --------------------------------------------
import asyncio
import uuid
from dataclasses import asdict
from temporalio.client import Client
from ai_mcp_onboarding_demo import CustomerInfo  # Import your dataclass workflow input

async def main():
    print("\n🚀 Connecting to Temporal Server...")
    client = await Client.connect("localhost:7233")
    print("✅ Connected to Temporal")

    # --------------------------------------------
    # Create test customer payload with sample document images
    # --------------------------------------------
    customer_data = CustomerInfo(
        customer_id=str(uuid.uuid4()),
        name="John Doe",
        email="john.doe@gmail.com",
        phone="1234567890",
        driver_license_image="driver_license_image_base64_or_path",
        passport_image="passport_image_base64_or_path",
        utility_bill_image="utility_bill_image_base64_or_path"
    )

    print("\n📦 Payload created:", asdict(customer_data))

    # --------------------------------------------
    # Execute Workflow
    # --------------------------------------------
    print("\n🧠 Starting CustomerOnboardingAIWorkflowMCP...")

    result = await client.execute_workflow(
        workflow="CustomerOnboardingAIWorkflowMCP",
        args=[customer_data],
        id=f"onboarding-{customer_data.customer_id}",
        task_queue="ai-onboarding-demo-task-queue"
    )

    print("\n🎉 Workflow completed successfully!")
    print("📄 Final Workflow Result:", result)

if __name__ == "__main__":
    asyncio.run(main())