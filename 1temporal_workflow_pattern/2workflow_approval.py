import asyncio
from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.worker import Worker

TASK_QUEUE = "customer-onboarding-queue"


# ---------------------------------------------------------
# Data Models
# ---------------------------------------------------------

@dataclass
class CustomerInfo:
    customer_id: str
    name: str
    email: str
    country: str


@dataclass
class ApprovalDecision:
    approval_status: str
    approver_id: str
    approver_role: str
    comments: Optional[str] = None


# ---------------------------------------------------------
# Activities
# ---------------------------------------------------------

@activity.defn
async def validate_customer_data(customer: CustomerInfo) -> bool:
    print(f"[Activity] Validating customer data for {customer.name}")

    await asyncio.sleep(1)
    return True


@activity.defn
async def create_approval_task(customer: CustomerInfo) -> str:
    """
    In real systems this would insert an approval task
    into a database or workflow task system.
    """
    print(f"[Activity] Creating approval task for {customer.name}")

    await asyncio.sleep(1)

    task_id = f"APPROVAL-{customer.customer_id}"
    print(f"[Activity] Approval task created: {task_id}")

    return task_id


@activity.defn
async def create_customer_account(customer: CustomerInfo) -> str:
    print(f"[Activity] Creating account for {customer.name}")

    await asyncio.sleep(2)

    account_id = f"ACCOUNT-{customer.customer_id}"
    print(f"[Activity] Account created: {account_id}")

    return account_id


@activity.defn
async def notify_customer_account(customer: CustomerInfo) -> str:
    print(f"[Activity] Notifying customer {customer.name}")

    await asyncio.sleep(1)

    notification_id = f"NOTIFY-{customer.customer_id}"
    print(f"[Activity] Notification sent: {notification_id}")

    return notification_id


# ---------------------------------------------------------
# Workflow
# ---------------------------------------------------------

@workflow.defn
class CustomerOnboardingWorkflow:

    def __init__(self):
        self.manager_approval: Optional[ApprovalDecision] = None

    # -----------------------------
    # Human Approval Signal
    # -----------------------------
    @workflow.signal
    def manager_approval(self, decision: ApprovalDecision):

        print(
            f"Approval received from {decision.approver_id}"
        )

        self.manager_approval = decision

    # -----------------------------
    # Workflow Query (optional)
    # -----------------------------
    @workflow.query
    def approval_status(self) -> str:

        if self.manager_approval is None:
            return "WAITING_FOR_APPROVAL"

        if self.manager_approval.approved:
            return "APPROVED"

        return "REJECTED"

    # -----------------------------
    # Workflow Execution
    # -----------------------------
    @workflow.run
    async def run(self, customer: CustomerInfo) -> str:

        print("Workflow started")

        # -----------------------------------
        # STEP 1: Validate Customer
        # -----------------------------------

        await workflow.execute_activity(
            validate_customer_data,
            customer,
            start_to_close_timeout=timedelta(seconds=10),
        )

        print("Customer validation completed")

        # -----------------------------------
        # STEP 2: Create Approval Task
        # -----------------------------------

        approval_task_id = await workflow.execute_activity(
            create_approval_task,
            customer,
            start_to_close_timeout=timedelta(seconds=10),
        )

        print(
            f"Waiting for manager approval (task={approval_task_id})"
        )

        # -----------------------------------
        # STEP 3: Wait for Human Approval
        # -----------------------------------

        await workflow.wait_condition(
            lambda: self.manager_approval is not None
        )

        if not self.manager_approval.approval_status == "APPROVED":

            print(
                f"Customer rejected by {self.manager_approval.approver_id}"
            )

            return "Customer onboarding rejected"

        print(
            f"Customer approved by {self.manager_approval.approver_id}"
        )

        # -----------------------------------
        # STEP 4: Create Customer Account
        # -----------------------------------

        account_id = await workflow.execute_activity(
            create_customer_account,
            customer,
            start_to_close_timeout=timedelta(seconds=10),
        )

        # -----------------------------------
        # STEP 5: Notify Customer
        # -----------------------------------

        await workflow.execute_activity(
            notify_customer_account,
            customer,
            start_to_close_timeout=timedelta(seconds=10),
        )

        return f"Customer account created: {account_id}"


# ---------------------------------------------------------
# Worker + Workflow Starter
# ---------------------------------------------------------

async def main():

    client = await Client.connect("localhost:7233")

    async with Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[CustomerOnboardingWorkflow],
        activities=[
            validate_customer_data,
            create_approval_task,
            create_customer_account,
            notify_customer_account,
        ],
    ):

        customer = CustomerInfo(
            customer_id="CUST-100",
            name="Alice",
            email="alice@email.com",
            country="Australia",
        )

        workflow_id = f"customer-onboarding-{customer.customer_id}"

        result = await client.execute_workflow(
            CustomerOnboardingWorkflow.run,
            customer,
            id=workflow_id,
            task_queue=TASK_QUEUE,
        )

        print("Workflow Result:", result)


if __name__ == "__main__":
    asyncio.run(main())