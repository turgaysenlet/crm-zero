import logging
import uuid
from sqlite3 import Connection, Cursor
from typing import Optional

from pydantic import BaseModel

from src.core.objects.case import Case
from src.core.objects.case_comment import CaseComment
from src.core.reference.object_reference import ObjectReference
from src.db.case_comment_record import CaseCommentRecord
from src.db.database import Database

logging.basicConfig()
logger = logging.getLogger("CommentCreator")
logger.setLevel(logging.DEBUG)


class CommentCreator(BaseModel):
    db: Optional[Database] = None

    def connect_to_db(self) -> [Connection, Cursor]:
        if self.db is None:
            self.db = Database(db_name="database/crm.db")
        # Connect to database
        [db_conn, db_cursor] = self.db.connect()
        return db_conn, db_cursor

    def create_comment(self, sender_case: Case, comment_summary, comment_description):
        db_conn, db_cursor = self.connect_to_db()
        case1_comment_1: CaseComment = CaseComment(
            owner_id=ObjectReference(object_type_name="User", object_id=sender_case.owner_id.object_id),
            case_id=ObjectReference.from_object(sender_case),
            summary=comment_summary,
            description=comment_description)
        CaseCommentRecord.from_object(case1_comment_1).insert_to_db(db_conn, db_cursor)


if __name__ == "__main__":
    sender_case: Case = Case(
        owner_id=ObjectReference(object_type_name="User", object_id="2e47d004-1f30-4fb9-a525-c33046973216"),
        account_id=ObjectReference(object_type_name="Account", object_id="46faac41-9270-43e3-a395-8ef9082b8dfb"),
        summary="Case 2 - Sales",
        description="Case 2 - Description")
    sender_case.id = uuid.UUID("27564ee6-3042-46f2-bc24-f96182565d58")
    sender_case.case_number = "00000002"
    comment_creator: CommentCreator = CommentCreator(db=Database(db_name="../../database/crm.db"))
    comment_creator.create_comment(sender_case=sender_case, comment_summary="Summary",
                                   comment_description="description")
