from temporalio import workflow
from datetime import timedelta
import asyncio
import random

with workflow.unsafe.imports_passed_through():
    from domain.onboarding.cust_models import CustomerOnboardingInput, CustomerOnboardingState
    from domain.onboarding.cust_activities import (
        create_customer_record,
        call_kyc_api,
        call_credit_api,
        activate_account,
        onboarding_publish_event,
    )


@workflow.defn
class CustomerOnboardingWorkflow:
    """Workflow to onboard a new customer: create record, KYC, credit, activation, and publish event."""

    def __init__(self):
        self.timeout = timedelta(seconds=30)
        self.manual_approved = False

    @workflow.signal
    async def manual_approval(self):
        """Signal to manually approve a customer if KYC or credit fails."""
        print("✋ Manual approval signal received")
        self.manual_approved = True

    async def execute(self, activity, state: CustomerOnboardingState):
        """Execute an activity with standard timeout."""
        return await workflow.execute_activity(
            activity,
            state,
            start_to_close_timeout=self.timeout,
        )

    @workflow.run
    async def run(self, payload: CustomerOnboardingInput) -> CustomerOnboardingState:
        """Run the customer onboarding workflow end-to-end."""

        print(f"\n🚀 Starting onboarding workflow for Customer: {payload.customer_id}")
        state = CustomerOnboardingState(**payload.dict())

        # Step 1: Create customer record
        print("⏳ Step 1: Creating customer record in DB...")
        state = await self.execute(create_customer_record, state)
        await asyncio.sleep(0.2)

        # Step 2: Parallel KYC + Credit checks
        print("⏳ Step 2: Running parallel KYC and Credit checks...")
        kyc, credit = await asyncio.gather(
            workflow.execute_activity(call_kyc_api, state, start_to_close_timeout=self.timeout),
            workflow.execute_activity(call_credit_api, state, start_to_close_timeout=self.timeout),
        )
        state.kyc_passed = kyc.kyc_passed
        state.credit_score = credit.credit_score
        print(f"   ✔ KYC passed: {state.kyc_passed}, Credit score: {state.credit_score}")

        # Step 3: Conditional manual approval
        if not state.kyc_passed or state.credit_score < 650:
            print(f"⚠ Customer {state.customer_id} requires manual approval...")
            # await workflow.wait_condition(lambda: self.manual_approved)
            print(f"   ✔ Manual approval completed for {state.customer_id}")

        # Step 4: Activate account
        print("⏳ Step 4: Activating customer account...")
        state = await self.execute(activate_account, state)
        await asyncio.sleep(0.2)

        # Step 5: Publish onboarding event
        print("⏳ Step 5: Publishing onboarding event...")
        state = await self.execute(onboarding_publish_event, state)

        print(f"✅ Workflow finished: Customer {state.customer_id} ONBOARDED\n")
        return state