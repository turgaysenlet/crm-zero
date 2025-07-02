import logging
import time
import uuid
from sqlite3 import Cursor, Connection
from typing import Optional, Dict, Any

from pydantic import BaseModel

from src.core.objects.case import Case

logging.basicConfig()
logger = logging.getLogger("CaseRecord")
logger.setLevel(logging.DEBUG)


class CaseRecord(BaseModel):
    id: str
    case_number: str
    owner_id: str
    summary: str
    description: Optional[str] = None
    created_at: float = 0.0
    updated_at: float = 0.0
    commit_at: float = 0.0

    @classmethod
    def table_name(cls) -> str:
        return "Cases"

    @classmethod
    def table_definition(cls) -> str:
        return f'''{CaseRecord.table_name()} (
                id TEXT PRIMARY KEY,
                case_number TEXT UNIQUE NOT NULL,
                owner_id TEXT NOT NULL,
                summary TEXT NOT NULL,                
                description TEXT,
                created_at FLOAT,
                updated_at FLOAT,
                commit_at FLOAT             
            )
        '''

    @classmethod
    def table_fields(cls) -> str:
        return f'id, case_number, owner_id, summary, description, created_at, updated_at, commit_at'

    @classmethod
    def get_last_case_number_query(cls) -> str:
        query = f"SELECT MAX(CAST(case_number AS INTEGER)) AS max_case_number FROM {CaseRecord.table_name()}"
        return query

    @classmethod
    def from_object(cls, obj: Case) -> "CaseRecord":
        return CaseRecord(
            id=str(obj.id),
            owner_id=str(obj.owner_id),
            case_number=obj.case_number,
            summary=obj.summary,
            description=obj.description,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            commit_at=obj.commit_at)

    @classmethod
    def from_db_row(cls, row: Dict) -> "CaseRecord":
        return CaseRecord(
            id=row["id"],
            owner_id=row["owner_id"],
            case_number=row["case_number"],
            summary=row["summary"],
            description=row.get("description", ""),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            commit_at=row["commit_at"]
        )

    def __init__(self, **data):
        super().__init__(**data)
        now = time.time()
        self.created_at = data.get("created_at", now)
        self.updated_at = data.get("updated_at", now)
        self.commit_at = data.get("commit_at", now)
        logger.debug(f"Creating case record: {self}")

    def insert_to_db(self, conn: Connection, cursor: Cursor):
        now = time.time()
        self.commit_at = now
        query = f"INSERT INTO {CaseRecord.table_name()} ({CaseRecord.table_fields()}) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        logger.debug(f'Running SQL query "{query}"')
        cursor.execute(
            query,
            (self.id, self.case_number, self.owner_id, self.summary, self.description, self.created_at, self.updated_at,
             self.commit_at)
        )
        conn.commit()

    def read_from_db_row(self, row: Dict[str, Any]) -> None:
        self.id = str(row["id"])
        self.owner_id = str(row["owner_id"])
        self.case_number = str(row["case_number"])
        self.summary = str(row["summary"])
        self.description = str(row.get("description", ""))
        self.created_at = float(row["created_at"])
        self.updated_at = float(row["updated_at"])
        self.commit_at = float(row["commit_at"])

    def read_from_object(self, obj: Case) -> None:
        self.id = str(obj.id)
        self.case_number = obj.case_number
        self.summary = obj.summary
        self.description = obj.description
        self.created_at = obj.created_at
        self.updated_at = obj.updated_at
        self.commit_at = obj.commit_at

    def convert_to_object(self) -> Case:
        obj: Case = Case(
            id=uuid.UUID(self.id),
            owner_id=uuid.UUID(self.owner_id),
            case_number=self.case_number,
            summary=self.summary,
            description=self.description,
            created_at=self.created_at,
            updated_at=self.updated_at,
            commit_at=self.commit_at
        )
        return obj
