import logging
import uuid
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, APIRouter, HTTPException, Query
from fastapi import Path as FastAPIPath
from nicegui import ui

from src.api.account_api_record import AccountApiRecord
from src.api.case_api_record import CaseApiRecord
from src.api.requests.account_create_request_api_record import AccountCreateRequestApiRecord
from src.api.requests.case_create_request_api_record import CaseCreateRequestApiRecord
from src.api.requests.workflow_step_update_request_api_record import WorkflowStepUpdateRequestApiRecord
from src.api.user_api_record import UserApiRecord
from src.api.workflow_api_record import WorkflowApiRecord
from src.api.workflow_step_api_record import WorkflowStepApiRecord
from src.api.workflow_trigger_api_record import WorkflowTriggerApiRecord
from src.core.access.user import User
from src.core.eventbus.workflow import Workflow
from src.core.eventbus.workflow_step import WorkflowStep
from src.core.eventbus.workflow_trigger import WorkflowTrigger
from src.core.objects.account import Account
from src.core.objects.case import Case
from src.db.account_record import AccountRecord
from src.db.case_record import CaseRecord
from src.db.database import Database
from src.db.user_record import UserRecord
from src.db.workflow_record import WorkflowRecord
from src.db.workflow_step_record import WorkflowStepRecord
from src.db.workflow_trigger_record import WorkflowTriggerRecord
from src.ui import create_case_page, workflow_editor_page

logging.basicConfig()
logger = logging.getLogger("Server")
logger.setLevel(logging.DEBUG)

app = FastAPI()


class Server:
    db: Database

    def __init__(self):
        logger.info("Initializing server")
        logger.info("Initializing database")
        self.init_db()
        logger.info("Initializing API router")
        self.router = APIRouter()
        logger.info("Adding API routes")
        # LIST
        self.router.add_api_route("/api/cases", self.get_cases_api_record, response_model=List[CaseApiRecord])
        self.router.add_api_route("/api/accounts", self.get_accounts_api_record, response_model=List[AccountApiRecord])
        self.router.add_api_route("/api/users", self.get_users_api_record, response_model=List[UserApiRecord])
        self.router.add_api_route("/api/workflows", self.get_workflows_api_record, response_model=List[WorkflowApiRecord])
        self.router.add_api_route("/api/workflow_steps", self.get_workflow_steps_api_record,
                                  response_model=List[WorkflowStepApiRecord])
        self.router.add_api_route("/api/workflow_triggers", self.get_workflow_trigger_api_record,
                                  response_model=List[WorkflowTriggerApiRecord])

        # LIST with access check
        self.router.add_api_route("/api/cases_by_username", self.get_cases_by_username, response_model=List[CaseApiRecord])
        # GET with id
        self.router.add_api_route("/api/cases/{case_id}", self.get_case_by_id_and_user, response_model=CaseApiRecord,
                                  methods=["GET"])
        self.router.add_api_route("/api/accounts/{account_id}", self.get_account_by_id_and_user,
                                  response_model=AccountApiRecord, methods=["GET"])
        self.router.add_api_route("/api/workflows/{workflow_id}", self.get_workflow_by_id,
                                  response_model=WorkflowApiRecord, methods=["GET"])
        self.router.add_api_route("/api/workflow_steps/{workflow_step_id}", self.get_workflow_step_by_id,
                                  response_model=WorkflowStepApiRecord, methods=["GET"])
        self.router.add_api_route("/api/workflow_steps/{workflow_step_id}", self.update_workflow_step_by_id,
                                  response_model=WorkflowStepApiRecord, methods=["POST"])

        self.router.add_api_route("/api/run/workflows/{workflow_id}", self.run_workflow_by_id,
                                  response_model=WorkflowApiRecord, methods=["GET"])

        self.router.add_api_route("/api/case", self.create_case, response_model=CaseApiRecord, methods=["POST"])
        self.router.add_api_route("/api/account", self.create_account, response_model=AccountApiRecord, methods=["POST"])

        logger.info(f"Done initializing server with {len(self.router.routes)} API routes defined")

    def init_db(self):
        # Connect to database
        self.db = Database(db_name="database/crm.db")
        [db_conn, db_cursor] = self.db.connect()
        self.db.init_db_schema(db_conn, db_cursor)
        # Reconnect after init_db_schema closes the db connection
        [db_conn, db_cursor] = self.db.connect()
        # Initialize workflow related object from database
        self.db.init_workflows_and_triggers(db_conn, db_cursor)

        # Grab the maximum case number from database
        # This is synced once per session, rest is incremented in memory per construction
        Case.last_case_number = self.db.read_max_case_number(db_conn, db_cursor)

        # Grab the maximum account number from database
        # This is synced once per session, rest is incremented in memory per construction
        Account.last_account_number = self.db.read_max_account_number(db_conn, db_cursor)

    async def get_cases_api_record(self) -> List[CaseApiRecord]:
        [db_conn, db_cursor] = self.db.connect()
        username = "admin"
        user: Optional[User] = await self.get_user(username)
        if user is None:
            db_conn.close()
            raise HTTPException(status_code=404, detail=f"User '{username}' not found.")
        else:
            case_records: List[CaseRecord] = self.db.read_objects(db_conn, db_cursor, CaseRecord.table_name(), "Case",
                                                                  user)
            cases: List[Case] = [case_record.convert_to_object() for case_record in case_records]
            case_api_records: List[CaseApiRecord] = [CaseApiRecord.from_object(_case) for _case in cases]
            if not case_api_records:
                db_conn.close()
                raise HTTPException(status_code=404, detail=f"No cases found.")
            db_conn.close()
            return case_api_records

    async def create_case(self, create_case_request: CaseCreateRequestApiRecord) -> CaseApiRecord:
        [db_conn, db_cursor] = self.db.connect()
        # TODO: Validate existence of owner_id and account_id in the database/live
        # TODO: Validate user access rules for create case
        # Create live case object
        case1: Case = create_case_request.create_case()
        # Commit to databasse
        case_record: CaseRecord = CaseRecord.from_object(case1)
        case_record.insert_to_db(db_conn, db_cursor)
        # Get the up-to-date database version of the object into memory object
        case1 = case_record.convert_to_object()
        case_api_record: CaseApiRecord = CaseApiRecord.from_object(case1)
        return case_api_record

    async def create_account(self, create_account_request: AccountCreateRequestApiRecord) -> AccountApiRecord:
        [db_conn, db_cursor] = self.db.connect()
        # TODO: Validate existence of owner_id in the database/live
        # TODO: Validate user access rules for create account
        # Create live account object
        account1: Account = create_account_request.create_account()
        # Commit to databasse
        account_record: AccountRecord = AccountRecord.from_object(account1)
        account_record.insert_to_db(db_conn, db_cursor)
        # Get the up-to-date database version of the object into memory object
        account1 = account_record.convert_to_object()
        account_api_record: AccountApiRecord = AccountApiRecord.from_object(account1)
        return account_api_record

    async def get_accounts_api_record(self) -> List[AccountApiRecord]:
        [db_conn, db_cursor] = self.db.connect()
        username = "admin"
        user: Optional[User] = await self.get_user(username)
        if user is None:
            db_conn.close()
            raise HTTPException(status_code=404, detail=f"User '{username}' not found.")
        else:
            account_records: List[AccountRecord] = self.db.read_objects(db_conn, db_cursor, AccountRecord.table_name(),
                                                                        "Account", user)
            accounts: List[Account] = [account_record.convert_to_object() for account_record in account_records]
            account_api_records: List[AccountApiRecord] = [AccountApiRecord.from_object(account) for account in
                                                           accounts]
            if not account_api_records:
                db_conn.close()
                raise HTTPException(status_code=404, detail=f"No account found.")
        db_conn.close()
        return account_api_records

    async def get_users_api_record(self) -> List[UserApiRecord]:
        [db_conn, db_cursor] = self.db.connect()
        user_records: List[UserRecord] = self.db.read_objects(db_conn, db_cursor, UserRecord.table_name(), "User", None)
        users: List[User] = [user_record.convert_to_object() for user_record in user_records]
        user_api_records: List[UserApiRecord] = [UserApiRecord.from_object(user) for user in users]
        if not user_api_records:
            db_conn.close()
            raise HTTPException(status_code=404, detail=f"No users found.")
        db_conn.close()
        return user_api_records

    async def get_user(self, username: str) -> Optional[User]:
        [db_conn, db_cursor] = self.db.connect()
        user_records: List[UserRecord] = self.db.read_objects(db_conn, db_cursor, UserRecord.table_name(), "User", None)
        all_profiles = self.db.get_profiles(db_conn, db_cursor)
        users: List[User] = [user_record.convert_to_object() for user_record in user_records]
        user = next((u for u in users if u.username == username), None)
        db_conn.close()
        return user

    async def get_workflows_api_record(self) -> List[WorkflowApiRecord]:
        [db_conn, db_cursor] = self.db.connect()
        workflow_records: List[WorkflowRecord] = self.db.read_objects(db_conn, db_cursor, WorkflowRecord.table_name(),
                                                                      "Workflow", None)
        workflows: List[Workflow] = [workflow_record.convert_to_object() for workflow_record in workflow_records]
        workflow_api_records: List[WorkflowApiRecord] = [WorkflowApiRecord.from_object(workflow) for
                                                         workflow in workflows]
        if not workflow_api_records:
            db_conn.close()
            raise HTTPException(status_code=404, detail=f"No workflows found.")
        db_conn.close()
        return workflow_api_records

    async def get_workflow_steps_api_record(self) -> List[WorkflowStepApiRecord]:
        [db_conn, db_cursor] = self.db.connect()
        workflow_step_records: List[WorkflowStepRecord] = self.db.read_objects(db_conn, db_cursor,
                                                                               WorkflowStepRecord.table_name(),
                                                                               "WorkflowStep", None)
        workflow_steps: List[WorkflowStep] = [workflow_step_record.convert_to_object() for workflow_step_record in
                                              workflow_step_records]
        workflow_step_api_records: List[WorkflowStepApiRecord] = [WorkflowStepApiRecord.from_object(workflow_step) for
                                                                  workflow_step in workflow_steps]
        if not workflow_step_api_records:
            db_conn.close()
            raise HTTPException(status_code=404, detail=f"No workflow steps found.")
        db_conn.close()
        return workflow_step_api_records

    async def get_workflow_trigger_api_record(self) -> List[WorkflowTriggerApiRecord]:
        [db_conn, db_cursor] = self.db.connect()
        workflow_trigger_records: List[WorkflowTriggerRecord] = self.db.read_objects(db_conn, db_cursor,
                                                                                     WorkflowTriggerRecord.table_name(),
                                                                                     "WorkflowTrigger", None)
        workflow_triggers: List[WorkflowTrigger] = [workflow_trigger_record.convert_to_object() for
                                                    workflow_trigger_record in workflow_trigger_records]
        workflow_trigger_api_records: List[WorkflowTriggerApiRecord] = [
            WorkflowTriggerApiRecord.from_object(workflow_trigger) for
            workflow_trigger in
            workflow_triggers]
        if not workflow_trigger_api_records:
            db_conn.close()
            raise HTTPException(status_code=404, detail=f"No workflow triggers found.")
        db_conn.close()
        return workflow_trigger_api_records

    async def get_workflow_steps_api_record(self) -> List[WorkflowStepApiRecord]:
        [db_conn, db_cursor] = self.db.connect()
        workflow_step_records: List[WorkflowStepRecord] = self.db.read_objects(db_conn, db_cursor,
                                                                               WorkflowStepRecord.table_name(),
                                                                               "WorkflowStep", None)
        workflow_steps: List[WorkflowStep] = \
            [workflow_step_record.convert_to_object() for workflow_step_record in workflow_step_records]
        workflow_step_api_records: List[WorkflowStepApiRecord] = \
            [WorkflowStepApiRecord.from_object(workflow_step) for workflow_step in workflow_steps]
        if not workflow_step_api_records:
            db_conn.close()
            raise HTTPException(status_code=404, detail=f"No workflow steps found.")
        db_conn.close()
        return workflow_step_api_records

    async def get_cases_by_username(self, username: str = Query(..., description="Username to filter cases by")) -> \
            List[CaseApiRecord]:
        user: Optional[User] = await self.get_user(username)
        [db_conn, db_cursor] = self.db.connect()
        if user is None:
            db_conn.close()
            raise HTTPException(status_code=404, detail=f"User '{username}' not found.")
        else:
            case_records: List[CaseRecord] = self.db.read_objects(db_conn, db_cursor, CaseRecord.table_name(), "Case",
                                                                  user)
            cases: List[Case] = [case_record.convert_to_object() for case_record in case_records]
            case_api_records: List[CaseApiRecord] = [CaseApiRecord.from_object(_case) for _case in cases]
            # Username based filtering
            # user_cases = [case for case in DUMMY_CASES if case.owner_id == username]
            if not case_api_records:
                db_conn.close()
                raise HTTPException(status_code=404, detail=f"No cases found for user '{username}'.")
            db_conn.close()
            return case_api_records

    async def get_case_by_id_and_user(
            self,
            case_id: uuid.UUID = FastAPIPath(..., description="Case ID (UUID)"),
            username: str = Query(..., description="Username to check access or ownership")
    ) -> CaseApiRecord:
        user: Optional[User] = await self.get_user(username)
        [db_conn, db_cursor] = self.db.connect()
        if user is None:
            db_conn.close()
            raise HTTPException(status_code=404, detail=f"User '{username}' not found.")
        else:
            case_record: CaseRecord = self.db.read_object_by_id(db_conn, db_cursor, CaseRecord.table_name(), "Case",
                                                                case_id, user)
            if not case_record:
                db_conn.close()
                raise HTTPException(status_code=404, detail=f"No case found for user '{username}'.")
            _case: Case = case_record.convert_to_object()
            case_api_record: CaseApiRecord = CaseApiRecord.from_object(_case)
            # Username based filtering
            # user_cases = [case for case in DUMMY_CASES if case.owner_id == username]
            if not case_api_record:
                db_conn.close()
                raise HTTPException(status_code=404, detail=f"No case found for user '{username}'.")
            db_conn.close()
            return case_api_record

    async def get_account_by_id_and_user(
            self,
            account_id: uuid.UUID = FastAPIPath(..., description="Account ID (UUID)"),
            username: str = Query(..., description="Username to check access or ownership")
    ) -> AccountApiRecord:
        user: Optional[User] = await self.get_user(username)
        [db_conn, db_cursor] = self.db.connect()
        if user is None:
            db_conn.close()
            raise HTTPException(status_code=404, detail=f"User '{username}' not found.")
        else:
            account_record: AccountRecord = self.db.read_object_by_id(db_conn, db_cursor, AccountRecord.table_name(),
                                                                      "Account", account_id, user)
            if not account_record:
                db_conn.close()
                raise HTTPException(status_code=404, detail=f"No account found for user '{username}'.")
            account: Account = account_record.convert_to_object()
            account_api_record: AccountApiRecord = AccountApiRecord.from_object(account)
            # Username based filtering
            # user_accounts = [account for account in DUMMY_ACCOUNTS if account.owner_id == username]
            if not account_api_record:
                db_conn.close()
                raise HTTPException(status_code=404, detail=f"No account found for user '{username}'.")
            db_conn.close()
            return account_api_record

    async def get_workflow_by_id(
            self,
            workflow_id: uuid.UUID = FastAPIPath(..., description="Workflow ID (UUID)")
    ) -> WorkflowApiRecord:
        [db_conn, db_cursor] = self.db.connect()

        workflow_record: WorkflowRecord = self.db.read_object_by_id(db_conn, db_cursor, WorkflowRecord.table_name(),
                                                                    "Workflow", workflow_id, None)
        if not workflow_record:
            db_conn.close()
            raise HTTPException(status_code=404, detail=f"No workflow found by id '{str(workflow_id)}'.")
        workflow: Workflow = workflow_record.convert_to_object()
        workflow_api_record: WorkflowApiRecord = WorkflowApiRecord.from_object(workflow)
        if not workflow_api_record:
            db_conn.close()
            raise HTTPException(status_code=404, detail=f"No workflow found by id '{str(workflow_id)}'.")
        db_conn.close()
        return workflow_api_record

    async def get_workflow_step_by_id(
            self,
            workflow_step_id: uuid.UUID = FastAPIPath(..., description="Workflow Step ID (UUID)")
    ) -> WorkflowStepApiRecord:
        [db_conn, db_cursor] = self.db.connect()

        workflow_step_record: WorkflowStepRecord = self.db.read_object_by_id(db_conn, db_cursor, WorkflowStepRecord.table_name(),
                                                                    "WorkflowStep", workflow_step_id, None)
        if not workflow_step_record:
            db_conn.close()
            raise HTTPException(status_code=404, detail=f"No workflow step found by id '{str(workflow_step_id)}'.")
        workflow_step: WorkflowStep = workflow_step_record.convert_to_object()
        workflow_step_api_record: WorkflowStepApiRecord = WorkflowStepApiRecord.from_object(workflow_step)
        if not workflow_step_api_record:
            db_conn.close()
            raise HTTPException(status_code=404, detail=f"No workflow step found by id '{str(workflow_step_id)}'.")
        db_conn.close()
        return workflow_step_api_record

    async def update_workflow_step_by_id(
            self,
            workflow_step_id: uuid.UUID = FastAPIPath(..., description="Workflow Step ID (UUID)"),
            update_request: WorkflowStepUpdateRequestApiRecord = None
    ) -> WorkflowStepApiRecord:
        [db_conn, db_cursor] = self.db.connect()

        workflow_step_record: WorkflowStepRecord = self.db.read_object_by_id(db_conn, db_cursor,
                                                                             WorkflowStepRecord.table_name(),
                                                                             "WorkflowStep", workflow_step_id, None)
        if not workflow_step_record:
            db_conn.close()
            raise HTTPException(status_code=404, detail=f"No workflow step found by id '{str(workflow_step_id)}'.")
        workflow_step: WorkflowStep = workflow_step_record.convert_to_object()
        # Apply update request
        update_request.update_workflow_step(workflow_step)
        # Write to database
        WorkflowStepRecord.from_object(workflow_step).insert_or_replace_to_db(db_conn, db_cursor)
        # TODO: Reread record from database
        workflow_step_api_record: WorkflowStepApiRecord = WorkflowStepApiRecord.from_object(workflow_step)
        if not workflow_step_api_record:
            db_conn.close()
            raise HTTPException(status_code=404, detail=f"No workflow step found by id '{str(workflow_step_id)}'.")
        # Reload all workflows, triggers and workflow steps to make them live
        self.db.init_workflows_and_triggers(db_conn, db_cursor)
        db_conn.close()
        return workflow_step_api_record

    async def run_workflow_by_id(
            self,
            workflow_id: uuid.UUID = FastAPIPath(..., description="Workflow ID (UUID)")
    ) -> WorkflowApiRecord:
        [db_conn, db_cursor] = self.db.connect()

        workflow_record: WorkflowRecord = self.db.read_object_by_id(db_conn, db_cursor, WorkflowRecord.table_name(),
                                                                    "Workflow", workflow_id, None)
        if not workflow_record:
            db_conn.close()
            raise HTTPException(status_code=404, detail=f"No workflow found by id '{str(workflow_id)}'.")
        workflow: Workflow = workflow_record.convert_to_object()
        # Read actual steps content
        workflow_steps: List[WorkflowStep] = []
        for workflow_step_id in workflow.workflow_step_ids.object_ids:
            workflow_step_record: WorkflowStepRecord = self.db.read_object_by_id(db_conn, db_cursor,
                                                                                 WorkflowStepRecord.table_name(),
                                                                                 "WorkflowStep", workflow_step_id,
                                                                                 None)
            workflow_steps.append(workflow_step_record.convert_to_object())
        # Set actual steps content to workflow before running it
        workflow.load_steps(workflow_steps)
        workflow.run_workflow(None, None)

        # Return record
        workflow_api_record: WorkflowApiRecord = WorkflowApiRecord.from_object(workflow)
        if not workflow_api_record:
            db_conn.close()
            raise HTTPException(status_code=404, detail=f"No workflow found by id '{str(workflow_id)}'.")
        db_conn.close()
        return workflow_api_record


# Mount the router
server = Server()
app.include_router(server.router)
ui.run_with(app, storage_secret="secret")

# To run:
if __name__ == "__main__":
    uvicorn.run("src.server.server:app", reload=True)
