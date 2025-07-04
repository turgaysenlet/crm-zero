import logging
import sys

from src.core.access.access_rule import AccessRule
from src.core.access.access_type import AccessType
from src.core.access.profile import Profile
from src.core.access.user import User
from src.core.eventbus.workflow import Workflow
from src.core.eventbus.workflow_step import WorkflowStep
from src.core.objects.account import Account
from src.core.objects.case import Case
from src.core.reference.object_reference import ObjectReference
from src.core.reference.object_reference_list import ObjectReferenceList
from src.db.account_record import AccountRecord

from src.db.database import Database
from src.db.case_record import CaseRecord
from src.db.profile_record import ProfileRecord
from src.db.user_record import UserRecord
from src.db.workflow_record import WorkflowRecord
from src.db.workflow_step_record import WorkflowStepRecord

logging.basicConfig()
logger = logging.getLogger("CLI Main")
logger.setLevel(logging.INFO)


def main(clean_db: bool = False):
    logger.debug("Starting CLI")
    logger.info("Welcome to CRM-Lite CLI")

    # Connect to database
    db: Database = Database(db_name="../database/crm.db")
    if clean_db:
        db.delete_if_exists()
    [db_conn, db_cursor] = db.connect()
    db.init_db_schema(db_conn, db_cursor)
    # Reconnect after init_db_schema closes the db connection
    [db_conn, db_cursor] = db.connect()

    # Read cases from database
    rows = db.list_table_rows(db_conn, db_cursor, CaseRecord.table_name())
    logger.info(f"Cases rows: {rows}")

    # Grab the maximum case number from database
    # This is synced once per session, rest is incremented in memory per construction
    Case.last_case_number = db.read_max_case_number(db_conn, db_cursor)

    # Grab the maximum account number from database
    # This is synced once per session, rest is incremented in memory per construction
    Account.last_account_number = db.read_max_account_number(db_conn, db_cursor)

    # Create live objects
    account_full_access: AccessRule = AccessRule(
        data_object_type="Account",
        access_type=AccessType.READ | AccessType.WRITE | AccessType.CREATE | AccessType.DELETE)
    case_full_access: AccessRule = AccessRule(
        data_object_type="Case",
        access_type=AccessType.READ | AccessType.WRITE | AccessType.CREATE | AccessType.DELETE)
    administrator_profile: Profile = Profile(name="Administrator", access_rules=[account_full_access, case_full_access])
    support_agent_profile: Profile = Profile(name="Support Agent", access_rules=[case_full_access])
    sales_agent_profile: Profile = Profile(name="Sales Agent", access_rules=[])
    administrator1: User = User(username="admin", fullname="Administrator",
                                profile_ids=ObjectReferenceList.from_list([administrator_profile]))
    support_agent_user1: User = User(username="jilljohns", fullname="Jill Johns",
                                     profile_ids=ObjectReferenceList.from_list([support_agent_profile]))
    sales_agent_user1: User = User(username="jackhills", fullname="Jack Hills",
                                   profile_ids=ObjectReferenceList.from_list([sales_agent_profile]))

    account1: Account = Account(account_name="Account 1",
                                owner_id=ObjectReference.from_object(support_agent_user1),
                                description="Account 1 - Description")

    workflow1_step: WorkflowStep = WorkflowStep(owner_id=ObjectReference.from_object(support_agent_user1),
                                                workflow_step_name="WorkflowStep1",
                                                workflow_step_code='print("Step1")')

    workflow2_step: WorkflowStep = WorkflowStep(owner_id=ObjectReference.from_object(support_agent_user1),
                                                workflow_step_name="WorkflowStep2",
                                                workflow_step_code='print("Step2")')

    workflow1: Workflow = Workflow(owner_id=ObjectReference.from_object(support_agent_user1),
                                   workflow_name="Workflow1",
                                   workflow_step_ids=ObjectReferenceList.from_list([workflow1_step, workflow2_step]))

    case1: Case = Case(owner_id=ObjectReference.from_object(support_agent_user1),
                       account_id=ObjectReference.from_object(account1),
                       summary="Case 1 - Support",
                       description="Case 1 - Description")
    case2: Case = Case(owner_id=ObjectReference.from_object(sales_agent_user1),
                       account_id=ObjectReference.from_object(account1),
                       summary="Case 2 - Sales",
                       description="Case 2 - Description")

    # Create and write database records for accounts
    WorkflowStepRecord.from_object(workflow1_step).insert_or_replace_to_db(db_conn, db_cursor)
    WorkflowStepRecord.from_object(workflow2_step).insert_or_replace_to_db(db_conn, db_cursor)

    WorkflowRecord.from_object(workflow1).insert_or_replace_to_db(db_conn, db_cursor)

    AccountRecord.from_object(account1).insert_or_replace_to_db(db_conn, db_cursor)

    # Create and write database records for cases
    CaseRecord.from_object(case1).insert_or_replace_to_db(db_conn, db_cursor)
    CaseRecord.from_object(case2).insert_or_replace_to_db(db_conn, db_cursor)

    # Create and write database records for profiles, but overwrite if exists
    ProfileRecord.from_object(administrator_profile).insert_or_replace_to_db(db_conn, db_cursor)
    ProfileRecord.from_object(support_agent_profile).insert_or_replace_to_db(db_conn, db_cursor)
    ProfileRecord.from_object(sales_agent_profile).insert_or_replace_to_db(db_conn, db_cursor)

    # Create and write database records for users, but overwrite if exists
    UserRecord.from_object(administrator1).insert_or_replace_to_db(db_conn, db_cursor)
    UserRecord.from_object(support_agent_user1).insert_or_replace_to_db(db_conn, db_cursor)
    UserRecord.from_object(sales_agent_user1).insert_or_replace_to_db(db_conn, db_cursor)

    support_agent_cases = db.read_objects(db_conn, db_cursor, CaseRecord.table_name(), "Case", support_agent_user1)
    logger.info(f"Cases readable by support agent (total: {len(support_agent_cases)}): "
                f"{[str(case) for case in support_agent_cases]}")
    sales_agent_cases = db.read_objects(db_conn, db_cursor, CaseRecord.table_name(), "Case", sales_agent_user1)
    logger.info(f"Cases readable by sales agent (total: {len(sales_agent_cases)}): "
                f"{[str(case) for case in sales_agent_cases]}")

    logger.debug("Stopping CLI")


if __name__ == "__main__":
    clean_db_param = False
    if "--clean_db" in sys.argv:
        logger.info(f"Cleaning database")
        clean_db_param = True
    main(clean_db_param)
