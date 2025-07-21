import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import timedelta

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

from src.core.access.access_rule import AccessRule
from src.core.access.access_type import AccessType
from src.core.access.profile import Profile
from src.core.access.user import User
from src.core.objects.account import Account
from src.core.objects.case import Case
from src.core.reference.object_reference import ObjectReference
from src.core.reference.object_reference_list import ObjectReferenceList


@dataclass
class CaseInput:
    case_json: str


# Basic activity that logs and does string concatenation
@activity.defn
def case_log_activity(input: CaseInput) -> str:
    activity.logger.info("Running activity with parameter %s" % input)
    _case = json.loads(input.case_json)
    return f"Case received by activity: {_case['case_number']} - {_case['summary']}"


# Basic workflow that logs and invokes an activity
@workflow.defn
class CaseWorkflow:
    @workflow.run
    async def run(self, case_json: str) -> str:
        workflow.logger.info("Running workflow with parameter %s" % case_json)
        return await workflow.execute_activity(
            case_log_activity,
            CaseInput(case_json=case_json),
            start_to_close_timeout=timedelta(seconds=10),
        )


async def run_temporal_workflow_async(_case: Case):
    # Start client
    client = await Client.connect("localhost:7233")

    # Run a worker for the workflow
    async with Worker(
            client,
            task_queue="case-activity-task-queue",
            workflows=[CaseWorkflow],
            activities=[case_log_activity],
            # Non-async activities require an executor;
            # a thread pool executor is recommended.
            # This same thread pool could be passed to multiple workers if desired.
            activity_executor=ThreadPoolExecutor(5),
    ):
        # While the worker is running, use the client to run the workflow and
        # print out its result. Note, in many production setups, the client
        # would be in a completely separate process from the worker.
        result = await client.execute_workflow(
            CaseWorkflow.run,
            _case.model_dump_json(),
            id="case-activity-workflow-id",
            task_queue="case-activity-task-queue",
        )
        print(f"Result: {result}")


async def main():
    import logging
    logging.basicConfig(level=logging.INFO)

    case_full_access: AccessRule = AccessRule(
        data_object_type="Case",
        access_type=AccessType.READ | AccessType.WRITE | AccessType.CREATE | AccessType.DELETE)
    support_agent_profile: Profile = Profile(name="Support Agent",
                                             access_rules=[case_full_access])
    support_agent_user1: User = User(username="jilljohns", fullname="Jill Johns",
                                     profile_ids=ObjectReferenceList.from_list([support_agent_profile]))
    account1: Account = Account(account_name="Account 1",
                                owner_id=ObjectReference.from_object(support_agent_user1),
                                description="Account 1 - Description")
    case1: Case = Case(owner_id=ObjectReference.from_object(support_agent_user1),
                       account_id=ObjectReference.from_object(account1),
                       summary="Where to enter medical details in a personal injure case",
                       description=
                       "I have a personal injure case that I need to enter the medical details into. "
                       "Which document do I enter these details to, like medical expenses, recovery times, etc.?")

    # Start client
    client = await Client.connect("localhost:7233")

    # Run a worker for the workflow
    async with Worker(
            client,
            task_queue="case-activity-task-queue",
            workflows=[CaseWorkflow],
            activities=[case_log_activity],
            # Non-async activities require an executor;
            # a thread pool executor is recommended.
            # This same thread pool could be passed to multiple workers if desired.
            activity_executor=ThreadPoolExecutor(5),
    ):
        # While the worker is running, use the client to run the workflow and
        # print out its result. Note, in many production setups, the client
        # would be in a completely separate process from the worker.
        result = await client.execute_workflow(
            CaseWorkflow.run,
            case1.model_dump_json(),
            id="case-activity-workflow-id",
            task_queue="case-activity-task-queue",
        )
        print(f"Result: {result}")


def run_temporal_workflow(_case: Case):
    asyncio.run(run_temporal_workflow_async(_case))


if __name__ == "__main__":
    asyncio.run(main())
