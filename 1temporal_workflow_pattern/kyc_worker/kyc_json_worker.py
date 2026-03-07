import asyncio
from datetime import timedelta
import json
from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.worker import Worker
import os

TEMPORAL_SERVER = os.getenv("TEMPORAL_SERVER", "localhost:7233")  # default for local dev

# -------------------------------
# Load workflow configuration from JSON
# -------------------------------
with open("kyc_workflow_config.json") as f:
    workflow_config = json.load(f)

# -------------------------------
# Activity Definitions
# -------------------------------
@activity.defn
async def validate_customer_info(customer_data: dict) -> bool:
    print(f"[Activity] Validating customer info: {customer_data}")
    return True

@activity.defn
async def verify_driver_license(customer_data: dict) -> bool:
    print(f"[Activity] Verifying driver license for {customer_data.get('customer_id')}")
    return True

@activity.defn
async def verify_passport(customer_data: dict) -> bool:
    print(f"[Activity] Verifying passport for {customer_data.get('customer_id')}")
    return True

@activity.defn
async def verify_address(customer_data: dict) -> bool:
    print(f"[Activity] Verifying address for {customer_data.get('customer_id')}")
    return True

@activity.defn
async def create_customer_account(customer_data: dict) -> str:
    print(f"[Activity] Creating customer account: {customer_data.get('customer_id')}")
    return f"account_{customer_data.get('customer_id')}"

@activity.defn
async def send_welcome_email(customer_data: dict) -> bool:
    print(f"[Activity] Sending welcome email to: {customer_data.get('email')}")
    return True

@activity.defn
async def notify_kyc_failure(customer_data: dict) -> bool:
    print(f"[Activity] KYC failed for {customer_data.get('customer_id')}. Notifying compliance.")
    return True

# Map activity names to functions
activity_map = {
    "validate_customer_info": validate_customer_info,
    "verify_driver_license": verify_driver_license,
    "verify_passport": verify_passport,
    "verify_address": verify_address,
    "create_customer_account": create_customer_account,
    "send_welcome_email": send_welcome_email,
    "notify_kyc_failure": notify_kyc_failure,
}

# -------------------------------
# Workflow Definition
# -------------------------------
@workflow.defn
class CustomerOnboardingWorkflow:
    @workflow.run
    async def run(self, customer_data: dict):
        results = {}

        for task in workflow_config["tasks"]:
            if task["type"] == "python_function":
                func = activity_map[task["function"]]
                result = await workflow.execute_activity(
                    func,
                    customer_data,
                    start_to_close_timeout=timedelta(seconds=30),
                )
                results[task["name"]] = result
                print(f"[Workflow] Task '{task['name']}' completed: {result}")

            elif task["type"] == "parallel":
                branch_coros = []
                for branch in task["branches"]:
                    branch_func = activity_map[branch["function"]]
                    branch_coros.append(
                        workflow.execute_activity(
                            branch_func,
                            customer_data,
                            start_to_close_timeout=timedelta(seconds=30),
                        )
                    )
                branch_results = await asyncio.gather(*branch_coros)
                results[task["name"]] = {
                    branch["name"]: res for branch, res in zip(task["branches"], branch_results)
                }
                print(f"[Workflow] Parallel task '{task['name']}' completed: {results[task['name']]}")

            elif task["type"] == "conditional":
                # Example condition: all KYC branches must pass
                if task["condition"] == "all_kyc_passed":
                    kyc_results = results.get("kyc_verification", {})
                    all_passed = all(kyc_results.values())
                    branch_key = "true_branch" if all_passed else "false_branch"
                    for branch_task in task[branch_key]:
                        func = activity_map[branch_task["function"]]
                        result = await workflow.execute_activity(
                            func,
                            customer_data,
                            start_to_close_timeout=timedelta(seconds=30),
                        )
                        results[branch_task["name"]] = result
                        print(f"[Workflow] Conditional task '{branch_task['name']}' executed: {result}")

        return results

# -------------------------------
# Worker Runner
# -------------------------------
async def main():
    # client = await Client.connect("localhost:7233")
    client = await Client.connect(TEMPORAL_SERVER)
    worker = Worker(
        client,
        task_queue="customer-onboarding-queue",
        workflows=[CustomerOnboardingWorkflow],
        activities=list(activity_map.values()),
    )
    print("Customer Onboarding Worker started...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())