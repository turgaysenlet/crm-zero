import logging
import time
import uuid
from sqlite3 import Cursor, Connection
from typing import Dict, Any

from pydantic import BaseModel

from src.core.eventbus.workflow import Workflow
from src.core.reference.object_reference import ObjectReference
from src.core.reference.object_reference_list import ObjectReferenceList

logging.basicConfig()
logger = logging.getLogger("WorkflowRecord")
logger.setLevel(logging.DEBUG)


class WorkflowRecord(BaseModel):
    id: str
    owner_id: str
    workflow_name: str
    workflow_step_ids: str
    created_at: float = 0.0
    updated_at: float = 0.0
    commit_at: float = 0.0
    object_type_name: str

    @classmethod
    def table_name(cls) -> str:
        return "Workflows"

    @classmethod
    def table_definition(cls) -> str:
        return f'''{WorkflowRecord.table_name()} (
                id TEXT PRIMARY KEY,
                owner_id TEXT NOT NULL,
                workflow_name TEXT UNIQUE NOT NULL,
                workflow_step_ids TEXT,
                created_at FLOAT,
                updated_at FLOAT,
                commit_at FLOAT,
                object_type_name TEXT NOT NULL
            )
        '''

    @classmethod
    def table_fields(cls) -> str:
        return f'id, owner_id, workflow_name, workflow_step_ids, created_at, updated_at, commit_at, object_type_name'

    @classmethod
    def from_object(cls, obj: Workflow) -> "WorkflowRecord":
        workflow_step_ids = "{}"
        if obj.workflow_step_ids is not None:
            workflow_step_ids = obj.workflow_step_ids.to_json_string()
        return WorkflowRecord(
            id=str(obj.id),
            owner_id=obj.owner_id.to_json_str(),
            workflow_name=str(obj.workflow_name),
            workflow_step_ids=workflow_step_ids,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            commit_at=obj.commit_at,
            object_type_name=obj.object_type_name
        )

    @classmethod
    def from_db_row(cls, row: Dict) -> "WorkflowRecord":
        return WorkflowRecord(
            id=row["id"],
            owner_id=row["owner_id"],
            workflow_name=row["workflow_name"],
            workflow_step_ids=row.get("workflow_step_ids", ""),
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
        logger.debug(f"Creating workflow record: {self}")

    def insert_to_db(self, conn: Connection, cursor: Cursor) -> None:
        now = time.time()
        self.commit_at = now
        query = f"INSERT INTO {WorkflowRecord.table_name()} ({WorkflowRecord.table_fields()}) " \
                f"VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        logger.debug(f'Running SQL query "{query}"')
        cursor.execute(
            query,
            (self.id, self.owner_id, self.workflow_name, self.workflow_step_ids, self.created_at, self.updated_at,
             self.commit_at, self.object_type_name)
        )
        conn.commit()

    def insert_or_replace_to_db(self, conn: Connection, cursor: Cursor):
        now = time.time()
        self.commit_at = now
        query = f"INSERT OR REPLACE INTO {WorkflowRecord.table_name()} ({WorkflowRecord.table_fields()}) " \
                f"VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        logger.debug(f'Running SQL query "{query}"')
        cursor.execute(
            query,
            (self.id, self.owner_id, self.workflow_name, self.workflow_step_ids, self.created_at, self.updated_at,
             self.commit_at, self.object_type_name)
        )
        conn.commit()

    def read_from_db_row(self, row: Dict[str, Any]) -> None:
        self.id = str(row["id"])
        self.owner_id = str(row["owner_id"])
        self.workflow_name = row["workflow_name"]
        self.workflow_step_ids = row.get("workflow_step_ids", "")
        self.created_at = float(row["created_at"])
        self.updated_at = float(row["updated_at"])
        self.commit_at = float(row["commit_at"])
        self.object_type_name = row["object_type_name"]

    def read_from_object(self, obj: Workflow) -> None:
        workflow_step_ids = "{}"
        if obj.profile_ids is not None:
            workflow_step_ids = obj.workflow_step_ids.to_json_string()
        self.id = str(obj.id)
        self.owner_id = obj.owner_id.to_json_str()
        self.workflow_name = obj.workflow_name
        self.workflow_step_ids = workflow_step_ids
        self.created_at = obj.created_at
        self.updated_at = obj.updated_at
        self.commit_at = obj.commit_at
        self.object_type_name = obj.object_type_name

    def convert_to_object(self) -> Workflow:
        obj: Workflow = Workflow(
            id=uuid.UUID(self.id),
            owner_id=ObjectReference.from_json_string(self.owner_id),
            workflow_name=self.workflow_name,
            workflow_step_ids=ObjectReferenceList.from_string(self.workflow_step_ids),
            created_at=self.created_at,
            updated_at=self.updated_at,
            commit_at=self.commit_at,
            object_type_name=self.object_type_name
        )
        return obj
