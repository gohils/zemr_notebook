import asyncio
from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.worker import Worker


TASK_QUEUE = "customer-onboarding-queue"


# ---------------------------------------------------------
# Data Model
# ---------------------------------------------------------

@dataclass
class CustomerInfo:
    customer_id: str
    name: str
    email: str
    country: str


# ---------------------------------------------------------
# Activities
# ---------------------------------------------------------

@activity.defn
async def validate_customer_data(customer: CustomerInfo) -> bool:
    print(f"Validating customer data for {customer.name}")

    if "@" not in customer.email:
        raise Exception("Invalid email")

    return True


@activity.defn
async def create_customer_account(customer: CustomerInfo) -> str:
    print(f"Creating account for {customer.name}")
    await asyncio.sleep(2)
    # Simulate account creation
    return f"ACCOUNT-{customer.customer_id}"

@activity.defn
async def notify_customer_account(customer: CustomerInfo) -> str:
    print(f"Notifying customer about account creation: {customer.name}")
    await asyncio.sleep(2)
    # Simulate notification
    return f"NOTIFICATION-{customer.customer_id}"

# ---------------------------------------------------------
# Workflow
# ---------------------------------------------------------

@workflow.defn
class CustomerOnboardingWorkflow:

    def __init__(self):
        self.approval_result: Optional[bool] = None

    # -----------------------------
    # Human Approval Signal
    # -----------------------------
    @workflow.signal
    def manager_approval(self, approved: bool):
        print(f"Received approval signal: {approved}")
        self.approval_result = approved

    # -----------------------------
    # Workflow Execution
    # -----------------------------
    @workflow.run
    async def run(self, customer: CustomerInfo) -> str:

        print("Workflow started")

        # -----------------------------------
        # STEP 1: Validate Customer Data
        # -----------------------------------

        await workflow.execute_activity(
            validate_customer_data,
            customer,
            start_to_close_timeout=timedelta(seconds=10),
        )

        print("Customer validation completed")

        # -----------------------------------
        # STEP 2: Human Approval
        # -----------------------------------

        print("Waiting for manager approval...")

        await workflow.wait_condition(
            lambda: self.approval_result is not None
        )

        if not self.approval_result:
            print("Customer rejected by manager")
            return "Customer onboarding rejected"

        print("Customer approved by manager")

        # -----------------------------------
        # STEP 3: Create Account
        # -----------------------------------

        account_id = await workflow.execute_activity(
            create_customer_account,
            customer,
            start_to_close_timeout=timedelta(seconds=10),
        )

        print(f"Customer account created: {account_id}")

        return f"Customer account created: {account_id}"


# ---------------------------------------------------------
# Main Worker
# ---------------------------------------------------------

async def main():

    client = await Client.connect("localhost:7233")

    async with Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[CustomerOnboardingWorkflow],
        activities=[validate_customer_data, create_customer_account, notify_customer_account],
    ):

        customer = CustomerInfo(
            customer_id="CUST-100",
            name="Alice",
            email="alice@email.com",
            country="Australia",
        )

        result = await client.execute_workflow(
            CustomerOnboardingWorkflow.run,
            customer,
            id="customer-onboarding-workflow-cust-100",
            task_queue=TASK_QUEUE,
        )

        print("Workflow Result:", result)


if __name__ == "__main__":
    asyncio.run(main())