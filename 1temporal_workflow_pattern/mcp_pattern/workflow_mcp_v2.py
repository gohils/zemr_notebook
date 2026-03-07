# workflow_mcp_v2.py
import asyncio
from dataclasses import dataclass
from datetime import timedelta
from typing import Dict, Any

from temporalio import workflow, activity
from temporalio.worker import Worker
from temporalio.client import Client as TemporalClient

# -------------------------------
# Input Data Class
# -------------------------------
@dataclass
class CustomerOnboardingInput:
    customer_id: str
    email: str
    mcp_url: str
    welcome_message: str = "Welcome! Your account is ready."

# -------------------------------
# Activities (non-deterministic imports)
# -------------------------------
@activity.defn
async def create_customer(input_data: CustomerOnboardingInput) -> Dict[str, Any]:
    """Call MCP to create a customer."""
    from fastmcp import Client as MCPClient

    async with MCPClient(input_data.mcp_url) as client:
        result = await client.call_tool(
            "create_customer",
            {"customer_id": input_data.customer_id, "email": input_data.email}
        )
    print(f"✅ create_customer result: {result.data}")
    return result.data

@activity.defn
async def verify_identity(input_data: CustomerOnboardingInput) -> Dict[str, Any]:
    """Call MCP to verify customer identity."""
    from fastmcp import Client as MCPClient

    async with MCPClient(input_data.mcp_url) as client:
        result = await client.call_tool(
            "verify_identity",
            {"customer_id": input_data.customer_id}
        )
    print(f"✅ verify_identity result: {result.data}")
    return result.data

@activity.defn
async def assign_account_manager(input_data: CustomerOnboardingInput) -> Dict[str, Any]:
    """Assign a default account manager via MCP."""
    from fastmcp import Client as MCPClient

    async with MCPClient(input_data.mcp_url) as client:
        result = await client.call_tool(
            "assign_account_manager",
            {"customer_id": input_data.customer_id, "manager_name": "Default Manager"}
        )
    print(f"✅ assign_account_manager result: {result.data}")
    return result.data

@activity.defn
async def initialize_erp_account(input_data: CustomerOnboardingInput) -> Dict[str, Any]:
    """Initialize ERP account for the customer."""
    from fastmcp import Client as MCPClient

    async with MCPClient(input_data.mcp_url) as client:
        result = await client.call_tool(
            "initialize_erp_account",
            {"customer_id": input_data.customer_id}
        )
    print(f"✅ initialize_erp_account result: {result.data}")
    return result.data

@activity.defn
async def notify_customer(input_data: CustomerOnboardingInput) -> Dict[str, Any]:
    """Send welcome notification to customer."""
    from fastmcp import Client as MCPClient

    async with MCPClient(input_data.mcp_url) as client:
        result = await client.call_tool(
            "notify_customer",
            {"customer_id": input_data.customer_id, "message": input_data.welcome_message}
        )
    print(f"✅ notify_customer result: {result.data}")
    return result.data

@activity.defn
async def get_customer(input_data: CustomerOnboardingInput) -> Dict[str, Any]:
    """Retrieve final customer record."""
    from fastmcp import Client as MCPClient

    async with MCPClient(input_data.mcp_url) as client:
        result = await client.call_tool(
            "get_customer",
            {"customer_id": input_data.customer_id}
        )
    print(f"✅ get_customer result: {result.data}")
    return result.data

# -------------------------------
# Workflow
# -------------------------------
with workflow.unsafe.imports_passed_through():
    pass  # No extra imports required

@workflow.defn
class CustomerOnboardingWorkflow:
    """Workflow-local state pattern for customer onboarding."""

    def __init__(self):
        # Store results of each activity in workflow-local state
        self.results: Dict[str, Any] = {}

    @workflow.run
    async def run(self, input_data: CustomerOnboardingInput) -> Dict[str, Any]:
        """
        Workflow sequence:
        1. Create customer
        2. Verify identity
        3. Assign account manager
        4. Initialize ERP account
        5. Notify customer
        6. Get final customer record
        """

        # Step 1: Create customer
        self.results["create_customer"] = await workflow.execute_activity(
            create_customer,
            input_data,
            start_to_close_timeout=timedelta(seconds=60)
        )

        # Step 2: Verify identity
        self.results["verify_identity"] = await workflow.execute_activity(
            verify_identity,
            input_data,
            start_to_close_timeout=timedelta(seconds=60)
        )

        # Step 3: Assign account manager
        self.results["assign_account_manager"] = await workflow.execute_activity(
            assign_account_manager,
            input_data,
            start_to_close_timeout=timedelta(seconds=60)
        )

        # Step 4: Initialize ERP account
        self.results["initialize_erp_account"] = await workflow.execute_activity(
            initialize_erp_account,
            input_data,
            start_to_close_timeout=timedelta(seconds=60)
        )

        # Step 5: Notify customer
        self.results["notify_customer"] = await workflow.execute_activity(
            notify_customer,
            input_data,
            start_to_close_timeout=timedelta(seconds=60)
        )

        # Step 6: Get final customer record
        self.results["get_customer"] = await workflow.execute_activity(
            get_customer,
            input_data,
            start_to_close_timeout=timedelta(seconds=60)
        )

        # Return aggregated workflow-local state
        return self.results

# -------------------------------
# Worker to run the workflow
# -------------------------------
async def main():
    client = await TemporalClient.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue="onboarding-tq",
        workflows=[CustomerOnboardingWorkflow],
        activities=[
            create_customer,
            verify_identity,
            assign_account_manager,
            initialize_erp_account,
            notify_customer,
            get_customer
        ],
    )

    print("🔹 Worker running. Listening for workflow tasks...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())