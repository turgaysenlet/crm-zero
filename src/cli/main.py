import logging

from src.core.objects.case import Case

from src.db.database import Database
from src.db.case_record import CaseRecord

logging.basicConfig()
logger = logging.getLogger("CLI Main")
logger.setLevel(logging.INFO)


def main():
    logger.debug("Starting CLI")
    logger.info("Welcome to CRM-Lite CLI")

    # Create objects
    case1: Case = Case(owner_id="user_1", summary="Case 1 - Summary", description="Case 1 - Description")

    db: Database = Database(db_name="../../database/crm.db")
    db.init_db_schema()

    db.connect()

    case_record1: CaseRecord = CaseRecord.from_object(case1)
    case_record1.insert_to_db(db.conn, db.cursor)

    rows = db.list_table_rows("Cases")
    logger.info(f"Cases rows: {rows}")

    row = rows.__getitem__(0)
    case_record2: CaseRecord = CaseRecord.from_db_row(row)
    logger.info(f"case_record2: {case_record2}")

    logger.debug("Stopping CLI")


if __name__ == "__main__":
    main()
