from temporalio import activity, workflow
from pydantic import BaseModel, EmailStr
from datetime import timedelta
import asyncio
from typing import Optional

# ============================================================
# DATA MODELS
# ============================================================

class CustomerOnboardingRequest(BaseModel):
    """Input payload for starting customer onboarding workflow."""
    name: str
    email: EmailStr
    city: str
    phone: str
    age: int
    occupation: Optional[str] = None


class CustomerRecord(BaseModel):
    """Represents persisted customer record in database."""
    customer_id: str
    name: str
    email: EmailStr
    city: str
    phone: str
    age: int
    occupation: Optional[str]
    status: str


class KYCResult(BaseModel):
    """Represents response from KYC external API."""
    kyc_status: str
    risk_score: int


class CreditResult(BaseModel):
    """Represents response from credit bureau API."""
    credit_score: int


class OnboardingResponse(BaseModel):
    """Final response returned by onboarding workflow."""
    customer_id: str
    account_id: Optional[str] = None
    status: str
    risk_score: Optional[int] = None
    credit_score: Optional[int] = None


# ============================================================
# DB OPERATIONS
# ============================================================

@activity.defn
async def create_customer_record(customer_data: CustomerOnboardingRequest) -> CustomerRecord:
    """Simulate creating a customer record in DB. Returns CustomerRecord."""
    print("\n[DB] create_customer_record INPUT:", customer_data.model_dump())
    await asyncio.sleep(0.5)

    return CustomerRecord(
        customer_id="CUST-1001",
        name=customer_data.name,
        email=customer_data.email,
        city=customer_data.city,
        phone=customer_data.phone,
        age=customer_data.age,
        occupation=customer_data.occupation,
        status="CREATED",
    )


@activity.defn
async def update_customer_status(payload: dict) -> str:
    """Simulate updating customer status in DB. Expects a dict with customer_id and status."""
    print("\n[DB] update_customer_status INPUT:", payload)
    await asyncio.sleep(0.3)
    return payload["status"]


# ============================================================
# EXTERNAL API OPERATIONS
# ============================================================

@activity.defn
async def run_kyc_check(customer: CustomerRecord) -> KYCResult:
    """Simulate calling KYC external API."""
    print("\n[API] run_kyc_check INPUT:", customer.model_dump())
    await asyncio.sleep(1)
    return KYCResult(kyc_status="APPROVED", risk_score=40)


@activity.defn
async def run_credit_check(customer: CustomerRecord) -> CreditResult:
    """Simulate calling credit bureau API."""
    print("\n[API] run_credit_check INPUT:", customer.model_dump())
    await asyncio.sleep(1)
    return CreditResult(credit_score=720)


@activity.defn
async def provision_bank_account(customer: CustomerRecord) -> str:
    """Simulate provisioning a bank account via core banking API."""
    print("\n[API] provision_bank_account INPUT:", customer.model_dump())
    await asyncio.sleep(0.5)
    return "ACC-5550001"


# ============================================================
# WORKFLOW ORCHESTRATION
# ============================================================

@workflow.defn
class CustomerOnboardingWorkflow:
    """Reference pattern for implementing workflows with multiple control flows."""

    @workflow.run
    async def run(self, customer_input: CustomerOnboardingRequest) -> OnboardingResponse:
        """
        Orchestrates the entire onboarding lifecycle using:
        - Sequential steps
        - Parallel execution
        - Conditional branching
        - Loops (polling)
        - Timeouts
        """

        # -------------------- WORKFLOW START --------------------
        print("\n=== WORKFLOW STARTED WITH INPUT ===")
        print(customer_input.model_dump())

        # -------------------- 1️⃣ Sequential Step --------------------
        # Create customer record in DB before any further processing
        customer: CustomerRecord = await workflow.execute_activity(
            create_customer_record,
            customer_input,  # Single argument (Pydantic model)
            start_to_close_timeout=timedelta(seconds=5),
        )

        # -------------------- 2️⃣ Parallel Execution --------------------
        # Run KYC and credit check in parallel for efficiency
        kyc_future = workflow.execute_activity(
            run_kyc_check,
            customer,
            start_to_close_timeout=timedelta(seconds=10),
        )

        credit_future = workflow.execute_activity(
            run_credit_check,
            customer,
            start_to_close_timeout=timedelta(seconds=10),
        )

        kyc_result, credit_result = await asyncio.gather(kyc_future, credit_future)

        risk_score = kyc_result.risk_score
        credit_score = credit_result.credit_score

        # -------------------- 3️⃣ Conditional Branching --------------------
        # Reject high-risk or low-credit customers immediately
        if risk_score > 70:
            await workflow.execute_activity(
                update_customer_status,
                {"customer_id": customer.customer_id, "status": "REJECTED_HIGH_RISK"},
                start_to_close_timeout=timedelta(seconds=5),
            )
            return OnboardingResponse(
                customer_id=customer.customer_id,
                status="REJECTED_HIGH_RISK"
            )

        if credit_score < 600:
            await workflow.execute_activity(
                update_customer_status,
                {"customer_id": customer.customer_id, "status": "REJECTED_LOW_CREDIT"},
                start_to_close_timeout=timedelta(seconds=5),
            )
            return OnboardingResponse(
                customer_id=customer.customer_id,
                status="REJECTED_LOW_CREDIT"
            )

        # -------------------- 4️⃣ Loop / Polling --------------------
        # Poll KYC until approved or max attempts reached
        attempt = 0
        max_attempts = 3
        kyc_status = kyc_result.kyc_status

        while kyc_status == "PENDING" and attempt < max_attempts:
            attempt += 1
            workflow.logger.info(f"KYC polling attempt {attempt}")
            await workflow.sleep(timedelta(seconds=3))

            kyc_result = await workflow.execute_activity(
                run_kyc_check,
                customer,
                start_to_close_timeout=timedelta(seconds=10),
            )
            kyc_status = kyc_result.kyc_status

        if kyc_status != "APPROVED":
            await workflow.execute_activity(
                update_customer_status,
                {"customer_id": customer.customer_id, "status": "REJECTED_KYC"},
                start_to_close_timeout=timedelta(seconds=5),
            )
            return OnboardingResponse(
                customer_id=customer.customer_id,
                status="REJECTED_KYC"
            )

        # -------------------- 5️⃣ Sequential — Provision Account --------------------
        # Once KYC & Credit pass, provision account
        account_id = await workflow.execute_activity(
            provision_bank_account,
            customer,
            start_to_close_timeout=timedelta(seconds=5),
        )

        # -------------------- 6️⃣ Final DB Update --------------------
        # Mark customer as active
        await workflow.execute_activity(
            update_customer_status,
            {"customer_id": customer.customer_id, "status": "ACTIVE"},
            start_to_close_timeout=timedelta(seconds=5),
        )

        # -------------------- WORKFLOW END --------------------
        return OnboardingResponse(
            customer_id=customer.customer_id,
            account_id=account_id,
            status="ACTIVE",
            risk_score=risk_score,
            credit_score=credit_score,
        )
    
    
# worker code to execute the workflow
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.common import RetryPolicy
from datetime import timedelta

# # Import your workflow and activities
# from customer_onboarding_workflow import (
#     CustomerOnboardingWorkflow,
#     create_customer_record,
#     update_customer_status,
#     run_kyc_check,
#     run_credit_check,
#     provision_bank_account,
# )

# Define the task queue name
TASK_QUEUE = "customer-task-queue"

async def main():
    # Connect to Temporal server (default localhost:7233)
    client = await Client.connect("localhost:7233")

    # Start a worker to listen for workflows and activities
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[CustomerOnboardingWorkflow],
        activities=[
            create_customer_record,
            update_customer_status,
            run_kyc_check,
            run_credit_check,
            provision_bank_account,
        ],
    )

    print(f"Worker listening on task queue: {TASK_QUEUE}")
    # Run the worker indefinitely
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())