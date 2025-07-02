import logging

from src.core.access.access_rule import AccessRule
from src.core.access.access_type import AccessType
from src.core.access.profile import Profile
from src.core.access.user import User
from src.core.objects.case import Case

from src.db.database import Database
from src.db.case_record import CaseRecord
from src.db.profile_record import ProfileRecord
from src.db.user_record import UserRecord

logging.basicConfig()
logger = logging.getLogger("CLI Main")
logger.setLevel(logging.INFO)


def main():
    logger.debug("Starting CLI")
    logger.info("Welcome to CRM-Lite CLI")

    # Connect to database
    db: Database = Database(db_name="../database/crm.db")
    # db.delete_if_exists()
    db.init_db_schema()
    db.connect()

    # Read cases from database
    rows = db.list_table_rows(CaseRecord.table_name())
    logger.info(f"Cases rows: {rows}")

    # Grab the maximum case number from database
    # This is synced once per session, rest is incremented in memory per construction
    Case.last_case_number = db.read_max_case_number()

    # Create live objects
    case_full_access: AccessRule = AccessRule(
        data_object_type="Case",
        access_type=AccessType.READ | AccessType.WRITE | AccessType.CREATE | AccessType.DELETE)
    support_agent_profile: Profile = Profile(name="Support Agent", access_rules=[case_full_access])
    sales_agent_profile: Profile = Profile(name="Sales Agent", access_rules=[])
    support_agent_user1: User = User(username="jilljohns", fullname="Jill Johns", profiles=[support_agent_profile])
    sales_agent_user1: User = User(username="jackhills", fullname="Jack Hills", profiles=[sales_agent_profile])
    case1: Case = Case(owner_id=support_agent_user1.id, summary="Case 1 - Support", description="Case 1 - Description")
    case2: Case = Case(owner_id=sales_agent_user1.id, summary="Case 2 - Sales", description="Case 2 - Description")

    # Create and write database records for cases
    case_record1: CaseRecord = CaseRecord.from_object(case1)
    case_record1.insert_to_db(db.conn, db.cursor)
    case_record2: CaseRecord = CaseRecord.from_object(case2)
    case_record2.insert_to_db(db.conn, db.cursor)

    # Create and write database records for profiles, but overwrite if exists
    profile_record1: ProfileRecord = ProfileRecord.from_object(support_agent_profile)
    profile_record1.insert_or_replace_to_db(db.conn, db.cursor)
    profile_record2: ProfileRecord = ProfileRecord.from_object(sales_agent_profile)
    profile_record2.insert_or_replace_to_db(db.conn, db.cursor)

    # Create and write database records for users, but overwrite if exists
    user_record1: UserRecord = UserRecord.from_object(support_agent_user1)
    user_record1.insert_or_replace_to_db(db.conn, db.cursor)
    user_record2: UserRecord = UserRecord.from_object(sales_agent_user1)
    user_record2.insert_or_replace_to_db(db.conn, db.cursor)

    support_agent_cases = db.read_objects(CaseRecord.table_name(), "Case", support_agent_user1)
    logger.info(f"Cases readable by support agent (total: {len(support_agent_cases)}): "
                f"{[str(case) for case in support_agent_cases]}")
    sales_agent_cases = db.read_objects(CaseRecord.table_name(), "Case", sales_agent_user1)
    logger.info(f"Cases readable by sales agent (total: {len(sales_agent_cases)}): "
                f"{[str(case)  for case in sales_agent_cases]}")

    logger.debug("Stopping CLI")


if __name__ == "__main__":
    main()
