import asyncio
from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.worker import Worker

TASK_QUEUE = "customer-onboarding-queue"


# -----------------------------
# Data Models
# -----------------------------
@dataclass
class CustomerInfo:
    customer_id: str
    name: str
    email: str
    country: str


@dataclass
class ApprovalDetails:
    approval_status: str  # "APPROVED" or "REJECTED"
    approver_id: str
    approver_role: str
    comments: Optional[str] = None


# -----------------------------
# Activities
# -----------------------------
@activity.defn
async def validate_customer_data(customer: CustomerInfo) -> bool:
    print(f"[Activity] Validating customer data for {customer.name}")
    await asyncio.sleep(1)
    return True

@activity.defn
async def evaluate_auto_approval(customer: CustomerInfo) -> bool:
    print(f"[Activity] Evaluating approval rules for {customer.name}")
    await asyncio.sleep(1)
    # auto approval rule
    if customer.country == "Australia":
        print("Auto approval rule matched")
        return True

    return False

@activity.defn
async def create_approval_task(customer: CustomerInfo) -> str:
    print("""
    === APPROVAL TASK CREATED ===
    Customer ID: ...
    Assigned to: Manager
    Action: Approve / Reject
    """)
    await asyncio.sleep(1)
    return f"APPROVAL-TASK-{customer.customer_id}"


@activity.defn
async def create_customer_in_crm(customer: CustomerInfo) -> str:
    print(f"[Activity] Creating customer in CRM for {customer.name}")
    await asyncio.sleep(1)
    return f"CRM-ACCOUNT-{customer.customer_id}"

@activity.defn
async def create_billing_account_in_erp(customer: CustomerInfo) -> str:
    print(f"[Activity] Creating billing account for {customer.name}")
    await asyncio.sleep(1)
    return f"ERP-ACCOUNT-{customer.customer_id}"

@activity.defn
async def notify_customer_account(customer: CustomerInfo) -> str:
    print(f"[Activity] Notifying customer {customer.name} about account creation")
    await asyncio.sleep(1)
    return f"NOTIFY-{customer.customer_id}"

@activity.defn
async def notify_customer_rejection(customer: CustomerInfo) -> str:
    print(f"[Activity] Notifying customer {customer.name} about account rejection")
    await asyncio.sleep(1)
    return f"NOTIFY-REJECTION-{customer.customer_id}"

# -----------------------------
# Workflow
# -----------------------------
@workflow.defn
class CustomerOnboardingWorkflow:

    def __init__(self):
        self.human_approval: Optional[ApprovalDetails] = None

    # Human approval signal
    @workflow.signal
    def manager_approval(self, approval_decision: ApprovalDetails):
        print(f"Approval received from {approval_decision.approver_id}")
        self.human_approval = approval_decision

    # Optional query
    @workflow.query
    def approval_status(self) -> str:
        if self.human_approval is None:
            return "WAITING_FOR_APPROVAL"
        return self.human_approval.approval_status

    @workflow.run
    async def run(self, customer: CustomerInfo) -> str:
        print("Workflow started")

        # STEP 1: Validate customer
        await workflow.execute_activity(
            validate_customer_data,
            customer,
            start_to_close_timeout=timedelta(seconds=10),
        )
        print("Customer validation completed")

        # STEP 2: Check auto approval rules
        auto_approved = await workflow.execute_activity(
            evaluate_auto_approval,
            customer,
            start_to_close_timeout=timedelta(seconds=10),
        )

        if auto_approved:
            print("Customer auto-approved by rule engine")

            self.human_approval = ApprovalDetails(
                approval_status="APPROVED",
                approver_id="SYSTEM",
                approver_role="AUTO_RULE_ENGINE",
            )

        else:

            print("Customer requires manual approval")
            # STEP 3:Send approval request to manager and Wait for human approval signal
            approval_request = await workflow.execute_activity(
            create_approval_task, customer,
            start_to_close_timeout=timedelta(seconds=10),  )
            print(f"Approval request sent: {approval_request}")
            print("Waiting for manager approval...")
            await workflow.wait_condition(lambda: self.human_approval is not None)

            if self.human_approval.approval_status.upper() == "REJECTED":
                print(f"Customer rejected by {self.human_approval.approver_id}")
                        # STEP 5: Notify customer
                await workflow.execute_activity(
                    notify_customer_rejection,
                    customer,
                    start_to_close_timeout=timedelta(seconds=10),
                )

                return "Customer onboarding rejected"

            print(f"Customer approved by {self.human_approval.approver_id}")

        # STEP 4: customer account Parallel creation in CRM and ERP
        print("⏳ Step 4: Creating accounts in CRM and ERP...")
        crm_account_task = workflow.execute_activity(
            create_customer_in_crm,
            customer,
            start_to_close_timeout=timedelta(seconds=10),
        )

        erp_account_task = workflow.execute_activity(
            create_billing_account_in_erp,
            customer,
            start_to_close_timeout=timedelta(seconds=10),
        )

        crm_account_id, erp_account_id = await asyncio.gather(
            crm_account_task,
            erp_account_task
        )
        print(f"customer in CRM : {crm_account_id}, customer account in ERP: {erp_account_id}")

        # STEP 5: Notify customer
        await workflow.execute_activity(
            notify_customer_account,
            customer,
            start_to_close_timeout=timedelta(seconds=10),
        )

        return f"Customer account created: {crm_account_id}, {erp_account_id}"

async def start_workflow_instance():
    client = await Client.connect("localhost:7233")
    customer = CustomerInfo(
        customer_id="CUST-100",
        name="Alice",
        email="alice@email.com",
        country="USA",
    )

    workflow_id = f"customer-onboarding-{customer.customer_id}"

    handle = await client.start_workflow(
        CustomerOnboardingWorkflow.run,
        customer,
        id=workflow_id,
        task_queue=TASK_QUEUE,
    )

    print("Workflow started:", workflow_id)
    result = await handle.result()
    print("Workflow Result:", result)

# -----------------------------
# Worker + Workflow starter
# -----------------------------
async def main():
    client = await Client.connect("localhost:7233")

    async with Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[CustomerOnboardingWorkflow],
        activities=[
            validate_customer_data,
            evaluate_auto_approval,
            create_approval_task,
            create_customer_in_crm,
            create_billing_account_in_erp,
            notify_customer_account,
            notify_customer_rejection,
        ],
    ):
        
        print("Worker started, waiting for workflow tasks...")
        await start_workflow_instance()


if __name__ == "__main__":
    asyncio.run(main())