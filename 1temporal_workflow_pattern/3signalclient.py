import asyncio
from temporalio.client import Client

async def approve():
    client = await Client.connect("localhost:7233")
    workflow_id = "customer-onboarding-CUST-100"
    handle = client.get_workflow_handle(workflow_id)

    approval_details = {
        "approval_status": "APPROVED",  # # "APPROVED" or "REJECTED"
        "approver_id": "manager_001",
        "approver_role": "RiskManager",
        "comments": "KYC verified, ready to onboard"
    }

    await handle.signal(
        "manager_approval",
        approval_details
    )

    print(f"Approval sent to workflow {workflow_id}")


asyncio.run(approve())