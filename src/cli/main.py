import logging
import sys

from src.core.access.access_rule import AccessRule
from src.core.access.access_type import AccessType
from src.core.access.profile import Profile
from src.core.access.user import User
from src.core.eventbus.workflow import Workflow
from src.core.eventbus.workflow_step import WorkflowStep
from src.core.eventbus.workflow_trigger import WorkflowTrigger
from src.core.objects.account import Account
from src.core.objects.case import Case
from src.core.objects.case_comment import CaseComment
from src.core.reference.object_reference import ObjectReference
from src.core.reference.object_reference_list import ObjectReferenceList
from src.db.account_record import AccountRecord
from src.db.case_comment_record import CaseCommentRecord

from src.db.database import Database
from src.db.case_record import CaseRecord
from src.db.profile_record import ProfileRecord
from src.db.user_record import UserRecord
from src.db.workflow_record import WorkflowRecord
from src.db.workflow_step_record import WorkflowStepRecord
from src.db.workflow_trigger_record import WorkflowTriggerRecord

logging.basicConfig()
logger = logging.getLogger("CLI Main")
logger.setLevel(logging.INFO)


def main(clean_db: bool = False):
    logger.debug("Starting CLI")
    logger.info("Welcome to CRM-Lite CLI")

    # Connect to database
    db: Database = Database(db_name="database/crm.db")
    if clean_db:
        db.delete_if_exists()
    [db_conn, db_cursor] = db.connect()
    db.init_db_schema(db_conn, db_cursor)
    # Reconnect after init_db_schema closes the db connection
    [db_conn, db_cursor] = db.connect()
    # Initialize workflow related object from database
    db.init_workflows_and_triggers(db_conn, db_cursor)

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
    case_comment_full_access: AccessRule = AccessRule(
        data_object_type="CaseComment",
        access_type=AccessType.READ | AccessType.WRITE | AccessType.CREATE | AccessType.DELETE)
    administrator_profile: Profile = Profile(name="Administrator", access_rules=[account_full_access, case_full_access,
                                                                                 case_comment_full_access])
    support_agent_profile: Profile = Profile(name="Support Agent",
                                             access_rules=[case_full_access, case_comment_full_access])
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
    account2: Account = Account(account_name="Account 2",
                                owner_id=ObjectReference.from_object(support_agent_user1),
                                description="Account 2 - Description")

    workflow1_step: WorkflowStep = WorkflowStep(
        owner_id=ObjectReference.from_object(support_agent_user1),
        workflow_step_name="Step1-PrintEventSender",
        workflow_step_code=
        'print(f"Step1: {trigger.workflow_trigger_event_type} object of type '
        '{trigger.workflow_trigger_object_type_name} with id {sender.id}")')

    workflow2_step: WorkflowStep = WorkflowStep(
        owner_id=ObjectReference.from_object(support_agent_user1),
        workflow_step_name="Step2-EmailOnCaseOrAccountCreation",
        workflow_step_code='''
from src.util.email_sender import EmailSender
email_sender: EmailSender = EmailSender()

object_number: str = ""
summary: str = ""
if trigger.workflow_trigger_object_type_name == "Case":
    object_number = sender.case_number
    summary = f" - {sender.summary}"
elif trigger.workflow_trigger_object_type_name == "Account":
    object_number = sender.account_number    

email_sender.send_mail(
    receiver_email="turgaysenlet@gmail.com",
    subject=f"{trigger.workflow_trigger_event_type} {trigger.workflow_trigger_object_type_name} - {object_number} {summary}",
    body=f"{trigger.workflow_trigger_object_type_name} {trigger.workflow_trigger_object_type_name} - {object_number} - id: {sender.id}\\r\\n\\r\\n{sender}\\r\\n\\r\\nCRM-Zero")
''')

    workflow3_step: WorkflowStep = WorkflowStep(
        owner_id=ObjectReference.from_object(support_agent_user1),
        workflow_step_name="Step3-EmailOnCommentCreation",
        workflow_step_code='''
from src.util.email_sender import EmailSender
email_sender: EmailSender = EmailSender()

object_number: str = ""
summary: str = ""
object_number = f"{sender.case_id.object_id} - {sender.case_comment_number}"
summary = f" - {sender.summary}"

email_sender.send_mail(
    receiver_email="turgaysenlet@gmail.com",
    subject=f"{trigger.workflow_trigger_event_type} {trigger.workflow_trigger_object_type_name} - {object_number} {summary}",
    body=f"{trigger.workflow_trigger_object_type_name} {trigger.workflow_trigger_object_type_name} - {object_number} - id: {sender.id}\\r\\n\\r\\n{sender.description}\\r\\n\\r\\nCRM-Zero")
''')

    workflow4_step: WorkflowStep = WorkflowStep(
        owner_id=ObjectReference.from_object(support_agent_user1),
        workflow_step_name="Step4-AddCommentOnCaseCreation",
        workflow_step_code='''
from src.util.comment_creator import CommentCreator

comment_creator: CommentCreator = CommentCreator()
comment_creator.create_comment(sender_case=sender, comment_summary=f"Case created - {sender.case_number}",
                               comment_description=f"Case created - {sender.case_number}")
    ''')

    workflow5_step: WorkflowStep = WorkflowStep(
        owner_id=ObjectReference.from_object(support_agent_user1),
        workflow_step_name="Step5-AddAssistantAckCommentOnCaseCreation",
        workflow_step_code='''
from src.util.comment_creator import CommentCreator
from src.util.assistant import Assistant

assistant: Assistant = Assistant()
comment_creator: CommentCreator = CommentCreator()

ack_text: str = assistant.give_initial_acknowledgement(sender.summary)

comment_creator.create_comment(sender_case=sender, comment_summary=f"Case received - {sender.case_number}",
                               comment_description=f"Case received - {sender.case_number} - {ack_text}")
        ''')

    workflow6_step: WorkflowStep = WorkflowStep(
        owner_id=ObjectReference.from_object(support_agent_user1),
        workflow_step_name="Step6-RecordAndSuggestOnCaseCreation",
        workflow_step_code='''
from src.util.n8n import N8n
n8n: N8n = N8n(workflow="case-record-and-suggest-solution-with-lookup")
n8n.run_workflow(sender, "")
''')

    workflow7_step: WorkflowStep = WorkflowStep(
        owner_id=ObjectReference.from_object(support_agent_user1),
        workflow_step_name="Step7-TemporalWorkflowOnCaseCreation",
        workflow_step_code='''
from src.util.temporal_workflow import run_temporal_workflow
run_temporal_workflow(sender)
    ''')

    workflow1: Workflow = Workflow(owner_id=ObjectReference.from_object(support_agent_user1),
                                   workflow_name="Workflow1",
                                   workflow_step_ids=ObjectReferenceList.from_list(
                                       [workflow1_step, workflow2_step, workflow4_step, workflow5_step,
                                        workflow6_step, workflow7_step]))

    workflow2: Workflow = Workflow(owner_id=ObjectReference.from_object(support_agent_user1),
                                   workflow_name="Workflow2",
                                   workflow_step_ids=ObjectReferenceList.from_list(
                                       [workflow3_step]))

    workflow_trigger1: WorkflowTrigger = WorkflowTrigger(owner_id=ObjectReference.from_object(support_agent_user1),
                                                         workflow_trigger_object_type_name="Case",
                                                         workflow_trigger_event_type="CREATE",
                                                         workflow_to_run_id=ObjectReference.from_object(workflow1))

    workflow_trigger2: WorkflowTrigger = WorkflowTrigger(owner_id=ObjectReference.from_object(support_agent_user1),
                                                         workflow_trigger_object_type_name="Account",
                                                         workflow_trigger_event_type="CREATE",
                                                         workflow_to_run_id=ObjectReference.from_object(workflow1))

    workflow_trigger3: WorkflowTrigger = WorkflowTrigger(owner_id=ObjectReference.from_object(support_agent_user1),
                                                         workflow_trigger_object_type_name="CaseComment",
                                                         workflow_trigger_event_type="CREATE",
                                                         workflow_to_run_id=ObjectReference.from_object(workflow2))

    # Create and write database records for profiles, but overwrite if exists
    ProfileRecord.from_object(administrator_profile).insert_or_replace_to_db(db_conn, db_cursor)
    ProfileRecord.from_object(support_agent_profile).insert_or_replace_to_db(db_conn, db_cursor)
    ProfileRecord.from_object(sales_agent_profile).insert_or_replace_to_db(db_conn, db_cursor)

    # Create and write database records for users, but overwrite if exists
    UserRecord.from_object(administrator1).insert_or_replace_to_db(db_conn, db_cursor)
    UserRecord.from_object(support_agent_user1).insert_or_replace_to_db(db_conn, db_cursor)
    UserRecord.from_object(sales_agent_user1).insert_or_replace_to_db(db_conn, db_cursor)

    # Create and write database records for accounts
    WorkflowStepRecord.from_object(workflow1_step).insert_or_replace_to_db(db_conn, db_cursor)
    WorkflowStepRecord.from_object(workflow2_step).insert_or_replace_to_db(db_conn, db_cursor)
    WorkflowStepRecord.from_object(workflow3_step).insert_or_replace_to_db(db_conn, db_cursor)
    WorkflowStepRecord.from_object(workflow4_step).insert_or_replace_to_db(db_conn, db_cursor)
    WorkflowStepRecord.from_object(workflow5_step).insert_or_replace_to_db(db_conn, db_cursor)
    WorkflowStepRecord.from_object(workflow6_step).insert_or_replace_to_db(db_conn, db_cursor)
    WorkflowStepRecord.from_object(workflow7_step).insert_or_replace_to_db(db_conn, db_cursor)

    WorkflowRecord.from_object(workflow1).insert_or_replace_to_db(db_conn, db_cursor)
    WorkflowRecord.from_object(workflow2).insert_or_replace_to_db(db_conn, db_cursor)

    WorkflowTriggerRecord.from_object(workflow_trigger1).insert_or_replace_to_db(db_conn, db_cursor)
    WorkflowTriggerRecord.from_object(workflow_trigger2).insert_or_replace_to_db(db_conn, db_cursor)
    WorkflowTriggerRecord.from_object(workflow_trigger3).insert_or_replace_to_db(db_conn, db_cursor)

    AccountRecord.from_object(account1).insert_to_db(db_conn, db_cursor)
    AccountRecord.from_object(account2).insert_to_db(db_conn, db_cursor)

    # Enable all triggers for case and comment creations below
    db.init_workflows_and_triggers(db_conn, db_cursor)

    case1: Case = Case(owner_id=ObjectReference.from_object(support_agent_user1),
                       account_id=ObjectReference.from_object(account1),
                       summary="Where to enter medical details in a personal injure case",
                       description=
                       "I have a personal injure case that I need to enter the medical details into. "
                       "Which document do I enter these details to, like medical expenses, recovery times, etc.?")

    case2: Case = Case(owner_id=ObjectReference.from_object(sales_agent_user1),
                       account_id=ObjectReference.from_object(account1),
                       summary="How to file a complaint",
                       description=
                       "I was in an accident, but forgot to report it. Please help me! "
                       "How do I file a complaint to other parties involved in the accident?")

    case1_comment_1: CaseComment = CaseComment(owner_id=ObjectReference.from_object(support_agent_user1),
                                               case_id=ObjectReference.from_object(case1),
                                               summary="Comment1",
                                               description="Comment1 details")

    case1_comment_2: CaseComment = CaseComment(owner_id=ObjectReference.from_object(support_agent_user1),
                                               case_id=ObjectReference.from_object(case1),
                                               summary="Comment2",
                                               description="Comment2 details")


    # Create and write database records for cases
    CaseRecord.from_object(case1).insert_to_db(db_conn, db_cursor)
    CaseRecord.from_object(case2).insert_to_db(db_conn, db_cursor)

    # Create and write database records for case comments
    CaseCommentRecord.from_object(case1_comment_1).insert_to_db(db_conn, db_cursor)
    CaseCommentRecord.from_object(case1_comment_2).insert_to_db(db_conn, db_cursor)

    # Read cases from database
    rows = db.list_table_rows(db_conn, db_cursor, CaseRecord.table_name())
    logger.info(f"Cases rows: {rows}")

    support_agent_cases = db.read_objects(db_conn, db_cursor, CaseRecord.table_name(), "Case", support_agent_user1)
    logger.info(f"Cases readable by support agent (total: {len(support_agent_cases)}): "
                f"{[str(case) for case in support_agent_cases]}")
    sales_agent_cases = db.read_objects(db_conn, db_cursor, CaseRecord.table_name(), "Case", sales_agent_user1)
    logger.info(f"Cases readable by sales agent (total: {len(sales_agent_cases)}): "
                f"{[str(case) for case in sales_agent_cases]}")
    all_triggers = db.read_objects(db_conn, db_cursor, WorkflowTriggerRecord.table_name(), "WorkflowTrigger", None)
    logger.info(f"Workflow triggers (total: {len(all_triggers)}): {[str(trigger) for trigger in all_triggers]}")

    logger.debug("Stopping CLI")


if __name__ == "__main__":
    clean_db_param = False
    if "--clean_db" in sys.argv:
        logger.info(f"Cleaning database")
        clean_db_param = True
    main(clean_db_param)
