import os
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from domain.order.orderworkflow import OrderProcessingWorkflow
from domain.order.orderactivities import (
    read_order,
    validate_inventory,
    fraud_check,
    charge_payment,
    update_order_status,
    order_publish_event,
)
from domain.onboarding.cust_workflow import CustomerOnboardingWorkflow
from domain.onboarding.cust_activities import (
    create_customer_record,
    call_kyc_api,
    call_credit_api,
    activate_account,
    onboarding_publish_event,
)

TEMPORAL_SERVER = os.getenv("TEMPORAL_SERVER", "localhost:7233")
TASK_QUEUE = os.getenv("TEMPORAL_TASK_QUEUE", "demo-task-queue")


async def main():
    client = await Client.connect(TEMPORAL_SERVER)

    print(f"🎯 Worker starting, listening to task queue '{TASK_QUEUE}'...")

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[OrderProcessingWorkflow, CustomerOnboardingWorkflow],
        activities=[
            # Order activities
            read_order,
            validate_inventory,
            fraud_check,
            charge_payment,
            update_order_status,
            order_publish_event,
            # Onboarding activities
            create_customer_record,
            call_kyc_api,
            call_credit_api,
            activate_account,
            onboarding_publish_event,
        ],
    )

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())