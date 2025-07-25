import json
import logging
import sqlite3
import time
import uuid
from sqlite3 import Cursor, Connection
from typing import Optional, Dict, Any

from pydantic import BaseModel

from src.core.objects.case_comment import CaseComment
from src.core.reference.object_reference import ObjectReference

logging.basicConfig()
logger = logging.getLogger("CaseCommentRecord")
logger.setLevel(logging.DEBUG)


class CaseCommentRecord(BaseModel):
    id: str
    case_comment_number: str
    owner_id: str
    case_id: str
    summary: str
    description: Optional[str] = None
    created_at: float = 0.0
    updated_at: float = 0.0
    commit_at: float = 0.0
    object_type_name: str

    @classmethod
    def table_name(cls) -> str:
        return "CaseComments"

    @classmethod
    def table_definition(cls) -> str:
        return f'''{CaseCommentRecord.table_name()} (
                id TEXT PRIMARY KEY,
                case_comment_number TEXT NOT NULL,
                owner_id TEXT NOT NULL,
                case_id TEXT NOT NULL,
                summary TEXT NOT NULL,                
                description TEXT,
                created_at FLOAT,
                updated_at FLOAT,
                commit_at FLOAT,
                object_type_name TEXT NOT NULL
            )
        '''

    @classmethod
    def table_fields(cls) -> str:
        return f'id, case_comment_number, owner_id, case_id, summary, description, created_at, updated_at, ' \
               f'commit_at, object_type_name'

    @classmethod
    def get_last_case_comment_number_for_case_query(cls, case_id: str) -> str:
        query = f"SELECT MAX(CAST(case_comment_number AS INTEGER)) AS max_case_comment_number FROM " \
                f"{CaseCommentRecord.table_name()} WHERE case_id='{case_id}'"
        return query

    @classmethod
    def from_object(cls, obj: CaseComment) -> "CaseCommentRecord":
        return CaseCommentRecord(
            id=str(obj.id),
            case_comment_number=obj.case_comment_number,
            owner_id=obj.owner_id.to_json_str(),
            case_id=obj.case_id.to_json_str(),
            summary=obj.summary,
            description=obj.description,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            commit_at=obj.commit_at,
            object_type_name=obj.object_type_name
        )

    @classmethod
    def from_db_row(cls, row: Dict) -> "CaseCommentRecord":
        return CaseCommentRecord(
            id=row["id"],
            case_comment_number=row["case_comment_number"],
            owner_id=row["owner_id"],
            case_id=row["case_id"],
            summary=row["summary"],
            description=row.get("description", ""),
            created_at=float(row["created_at"]),
            updated_at=float(row["updated_at"]),
            commit_at=float(row["commit_at"]),
            object_type_name=row["object_type_name"]
        )

    def __init__(self, **data):
        super().__init__(**data)
        now = time.time()
        self.created_at = data.get("created_at", now)
        self.updated_at = data.get("updated_at", now)
        self.commit_at = data.get("commit_at", now)
        logger.debug(f"Creating case comment record: {self}")

    def insert_to_db(self, conn: Connection, cursor: Cursor) -> None:
        # case_id = json.loads(self.case_id)['object_id']
        max_case_comment_number: int = self.read_max_case_comment_number_for_case(conn, cursor, self.case_id)
        self.case_comment_number = CaseComment.case_comment_number_from_number(max_case_comment_number + 1)

        now = time.time()
        self.commit_at = now
        query = f"INSERT INTO {CaseCommentRecord.table_name()} ({CaseCommentRecord.table_fields()}) " \
                f"VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        logger.debug(f'Running SQL query "{query}"')
        cursor.execute(
            query,
            (self.id, self.case_comment_number, self.owner_id, self.case_id, self.summary, self.description,
             self.created_at, self.updated_at, self.commit_at, self.object_type_name)
        )
        conn.commit()

    def read_max_case_comment_number_for_case(self, conn: Connection, cursor: Cursor, case_id: str) -> int:
        max_case_comment_number: int = 0
        if not conn:
            logger.error("Database connection not established. Cannot list table.")
            return max_case_comment_number
        try:
            query = CaseCommentRecord.get_last_case_comment_number_for_case_query(case_id)
            logger.debug(f'Running SQL query "{query}"')
            cursor.execute(query)
            rows = cursor.fetchall()
            logger.debug(f'Received rows: "{rows}"')
            if len(rows) > 0:
                row = dict(rows[0])
                max_case_comment_number_value = row.get("max_case_comment_number", max_case_comment_number)
                if max_case_comment_number_value is None:
                    max_case_comment_number_value = max_case_comment_number
                logger.info(
                    f"Last case comment number in database is {max_case_comment_number_value} for case {case_id}.")
                return max_case_comment_number_value
            return max_case_comment_number
        except sqlite3.OperationalError as e:
            logger.error(f"Error: Table '{CaseCommentRecord.table_name()}' does not exist or SQL error. {e}")
            return max_case_comment_number
        except sqlite3.Error as e:
            logger.error(f"Error listing table '{CaseCommentRecord.table_name()}': {e}")
            return max_case_comment_number

    def read_from_db_row(self, row: Dict[str, Any]) -> None:
        self.id = str(row["id"])
        self.case_comment_number = str(row["case_comment_number"])
        self.owner_id = str(row["owner_id"])
        self.case_id = str(row["case_id"])
        self.summary = str(row["summary"])
        self.description = str(row.get("description", ""))
        self.created_at = float(row["created_at"])
        self.updated_at = float(row["updated_at"])
        self.commit_at = float(row["commit_at"])
        self.object_type_name = row["object_type_name"]

    def read_from_object(self, obj: CaseComment) -> None:
        self.id = str(obj.id)
        self.case_comment_number = obj.case_comment_number
        self.owner_id = obj.owner_id.to_json_str()
        self.case_id = obj.case_id.to_json_str()
        self.summary = obj.summary
        self.description = obj.description
        self.created_at = obj.created_at
        self.updated_at = obj.updated_at
        self.commit_at = obj.commit_at
        self.object_type_name = obj.object_type_name

    def convert_to_object(self) -> CaseComment:
        obj: CaseComment = CaseComment(
            id=uuid.UUID(self.id),
            case_comment_number=self.case_comment_number,
            owner_id=ObjectReference.from_json_string(self.owner_id),
            case_id=ObjectReference.from_json_string(self.case_id),
            summary=self.summary,
            description=self.description,
            created_at=self.created_at,
            updated_at=self.updated_at,
            commit_at=self.commit_at,
            object_type_name=self.object_type_name
        )
        return obj
