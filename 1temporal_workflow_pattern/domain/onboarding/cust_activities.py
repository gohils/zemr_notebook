import asyncio
import random
from temporalio import activity
from domain.onboarding.cust_models import CustomerOnboardingState


@activity.defn
async def create_customer_record(
    state: CustomerOnboardingState,
) -> CustomerOnboardingState:
    """Persist new customer record into onboarding database."""

    print("🗄 [DB WRITE] Creating customer record...")

    await asyncio.sleep(0.5)  # simulate DB latency

    state.customer_id = state.customer_id
    state.account_activated = False

    print(f"   ✔ Customer {state.customer_id} stored with status INITIATED")

    return state


@activity.defn
async def call_kyc_api(
    state: CustomerOnboardingState,
) -> CustomerOnboardingState:
    """Call external KYC provider API to verify identity."""

    print("🔎 [HTTP POST] Sending data to KYC provider...")

    await asyncio.sleep(1)  # simulate API latency

    # Simulate realistic KYC outcome
    state.kyc_passed = random.choice([True, True, True, False])

    print(f"   ✔ KYC result: {state.kyc_passed}")

    return state


@activity.defn
async def call_credit_api(
    state: CustomerOnboardingState,
) -> CustomerOnboardingState:
    """Fetch credit score from external credit bureau."""

    print("🏦 [HTTP GET] Requesting credit score from bureau...")

    await asyncio.sleep(1)

    state.credit_score = random.randint(600, 800)

    print(f"   ✔ Credit score received: {state.credit_score}")

    return state


@activity.defn
async def activate_account(
    state: CustomerOnboardingState,
) -> CustomerOnboardingState:
    """Activate customer account in core banking system."""

    print("✅ [DB UPDATE] Activating customer account...")

    await asyncio.sleep(0.5)

    state.account_activated = True

    print(f"   ✔ Customer {state.customer_id} account ACTIVATED")

    return state


@activity.defn
async def onboarding_publish_event(
    state: CustomerOnboardingState,
) -> CustomerOnboardingState:
    """Publish CUSTOMER_ACTIVATED event to message broker."""

    print("📢 [EVENT] Publishing CUSTOMER_ACTIVATED event...")

    await asyncio.sleep(0.3)

    print(f"   ✔ Event published for {state.customer_id}")

    return state