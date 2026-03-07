# ---------------------------------------
# CustomerOnboardingAIWorkflowMCP.py
# ---------------------------------------
import asyncio
from dataclasses import dataclass
from datetime import timedelta
from typing import List, Dict
from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.worker import Worker

TASK_QUEUE = "ai-onboarding-demo-task-queue"

# ---------------------------------------
# Input Model
# ---------------------------------------
@dataclass
class CustomerInfo:
    customer_id: str
    name: str
    email: str
    phone: str
    driver_license_image: str
    passport_image: str
    utility_bill_image: str

# ---------------------------------------
# Document Input Model for AI KYC
# ---------------------------------------
@dataclass
class DocumentInput:
    customer_id: str
    document_image: str

# ---------------------------------------
# Workflow State (persisted automatically by Temporal)
# ---------------------------------------
@dataclass
class OnboardingState:
    customer: CustomerInfo = None
    validation_passed: bool = False
    kyc_passed: bool = False
    fraud_passed: bool = False
    credit_score: int = 0
    account_id: str = ""
    notification_sent: bool = False

# =======================================
# Activities
# =======================================
@activity.defn
async def validate_customer(customer: CustomerInfo) -> bool:
    print("Activity: Validating customer info...")
    await asyncio.sleep(0.5)
    return (
        bool(customer.name.strip())
        and "@" in customer.email
        and customer.phone.isdigit()
    )

@activity.defn
async def verify_driver_license(doc_input: DocumentInput) -> Dict:
    print(f"Activity: Verifying driver's license for {doc_input.customer_id}...")
    await asyncio.sleep(0.5)
    # Simulate OCR and verification
    return {"doc_type": "driver_license", "verified": True, "text": "Driver License OCR text"}

@activity.defn
async def verify_passport(doc_input: DocumentInput) -> Dict:
    print(f"Activity: Verifying passport for {doc_input.customer_id}...")
    await asyncio.sleep(0.5)
    return {"doc_type": "passport", "verified": True, "text": "Passport OCR text"}

@activity.defn
async def verify_utility_bill(doc_input: DocumentInput) -> Dict:
    print(f"Activity: Verifying utility bill for {doc_input.customer_id}...")
    await asyncio.sleep(0.5)
    return {"doc_type": "utility_bill", "verified": True, "text": "Utility bill OCR text"}

@activity.defn
async def fraud_check_mcp(documents: List[Dict]) -> bool:
    print("Activity: Performing AI/MCP fraud check on documents...")
    await asyncio.sleep(0.5)
    # Simulate AI fraud detection logic
    print(f"Fraud check input documents: {documents}")
    return True  # Simulate passed

@activity.defn
async def credit_check(customer: CustomerInfo) -> int:
    print("Activity: Performing credit check...")
    await asyncio.sleep(0.5)
    return 750  # simulate score

@activity.defn
async def create_account(customer: CustomerInfo) -> str:
    print("Activity: Creating CRM account...")
    await asyncio.sleep(0.5)
    return "ACCT-123456"

@activity.defn
async def send_welcome_notification(name: str) -> bool:
    print(f"Activity: Sending welcome notification to {name}...")
    await asyncio.sleep(0.2)
    return True

# =======================================
# Workflow Definition
# =======================================
@workflow.defn
class CustomerOnboardingAIWorkflowMCP:

    def __init__(self):
        self.state = OnboardingState()

    @workflow.run
    async def run(self, customer: CustomerInfo) -> OnboardingState:

        # ---------------------------------------
        # Store input in workflow state
        # ---------------------------------------
        print("Workflow: Starting AI-powered onboarding process...")
        self.state.customer = customer

        # ---------------------------------------
        # 1️⃣ Sequential + Conditional Validation
        # ---------------------------------------
        print("Workflow: Validating customer details...")
        self.state.validation_passed = await workflow.execute_activity(
            validate_customer,
            customer,
            start_to_close_timeout=timedelta(seconds=5),
        )

        if not self.state.validation_passed:
            print("Workflow: Validation failed. Ending workflow.")
            return self.state

        # ---------------------------------------
        # 2️⃣ Parallel KYC Verification (Separate AI Activities)
        # ---------------------------------------
        print("Workflow: Running parallel KYC verification...")

        kyc_tasks = [
            workflow.execute_activity(
                verify_driver_license,
                DocumentInput(customer.customer_id, customer.driver_license_image),
                start_to_close_timeout=timedelta(seconds=5),
            ),
            workflow.execute_activity(
                verify_passport,
                DocumentInput(customer.customer_id, customer.passport_image),
                start_to_close_timeout=timedelta(seconds=5),
            ),
            workflow.execute_activity(
                verify_utility_bill,
                DocumentInput(customer.customer_id, customer.utility_bill_image),
                start_to_close_timeout=timedelta(seconds=5),
            ),
        ]

        kyc_results = await asyncio.gather(*kyc_tasks)
        self.state.kyc_passed = all(doc["verified"] for doc in kyc_results)

        if not self.state.kyc_passed:
            print("Workflow: KYC failed. Ending workflow.")
            return self.state

        # ---------------------------------------
        # 2️⃣b Fraud Check via AI/MCP
        # ---------------------------------------
        print("Workflow: Running fraud check on KYC documents...")
        self.state.fraud_passed = await workflow.execute_activity(
            fraud_check_mcp,
            kyc_results,
            start_to_close_timeout=timedelta(seconds=5),
        )

        if not self.state.fraud_passed:
            print("Workflow: Fraud check failed. Ending workflow.")
            return self.state

        # ---------------------------------------
        # 3️⃣ Loop Example (Retry-style credit check)
        # ---------------------------------------
        print("Workflow: Performing credit check with retry loop...")
        attempts = 0
        max_attempts = 3

        while attempts < max_attempts:
            self.state.credit_score = await workflow.execute_activity(
                credit_check,
                customer,
                start_to_close_timeout=timedelta(seconds=5),
            )
            if self.state.credit_score >= 700:
                print("Workflow: Credit approved.")
                break
            print("Workflow: Credit too low, retrying...")
            attempts += 1

        if self.state.credit_score < 700:
            print("Workflow: Credit check failed after retries.")
            return self.state

        # ---------------------------------------
        # 4️⃣ Sequential Account Creation
        # ---------------------------------------
        print("Workflow: Creating account...")
        self.state.account_id = await workflow.execute_activity(
            create_account,
            customer,
            start_to_close_timeout=timedelta(seconds=5),
        )

        # ---------------------------------------
        # 5️⃣ Final Notification
        # ---------------------------------------
        print("Workflow: Sending welcome notification...")
        self.state.notification_sent = await workflow.execute_activity(
            send_welcome_notification,
            customer.name,
            start_to_close_timeout=timedelta(seconds=5),
        )

        print("Workflow: AI-powered onboarding completed successfully!")
        return self.state

# =======================================
# Worker Runner
# =======================================
async def main():
    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[CustomerOnboardingAIWorkflowMCP],
        activities=[
            validate_customer,
            verify_driver_license,
            verify_passport,
            verify_utility_bill,
            fraud_check_mcp,
            credit_check,
            create_account,
            send_welcome_notification,
        ],
    )

    print(f"Worker started on task queue: {TASK_QUEUE}")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())