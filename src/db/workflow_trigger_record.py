import logging
import time
import uuid
from sqlite3 import Cursor, Connection
from typing import Dict, Any

from pydantic import BaseModel

from src.core.eventbus.workflow_trigger import WorkflowTrigger
from src.core.reference.object_reference import ObjectReference

logging.basicConfig()
logger = logging.getLogger("WorkflowRecord")
logger.setLevel(logging.DEBUG)


class WorkflowTriggerRecord(BaseModel):
    id: str
    owner_id: str
    workflow_trigger_object_type_name: str
    workflow_trigger_event_type: str
    created_at: float = 0.0
    updated_at: float = 0.0
    commit_at: float = 0.0
    object_type_name: str
    workflow_to_run_id: str

    @classmethod
    def table_name(cls) -> str:
        return "WorkflowTriggers"

    @classmethod
    def table_definition(cls) -> str:
        return f'''{WorkflowTriggerRecord.table_name()} (
                id TEXT PRIMARY KEY,
                owner_id TEXT NOT NULL,
                workflow_trigger_object_type_name TEXT NOT NULL,
                workflow_trigger_event_type TEXT NOT NULL,
                workflow_to_run_id TEXT NOT NULL,
                created_at FLOAT,
                updated_at FLOAT,
                commit_at FLOAT,
                object_type_name TEXT NOT NULL                
            )
        '''

    @classmethod
    def table_fields(cls) -> str:
        return f'id, owner_id, workflow_trigger_object_type_name, workflow_trigger_event_type, workflow_to_run_id, ' \
               f'created_at, updated_at, commit_at, object_type_name'

    @classmethod
    def from_object(cls, obj: WorkflowTrigger) -> "WorkflowTriggerRecord":
        return WorkflowTriggerRecord(
            id=str(obj.id),
            owner_id=obj.owner_id.to_json_str(),
            workflow_trigger_object_type_name=str(obj.workflow_trigger_object_type_name),
            workflow_trigger_event_type=obj.workflow_trigger_event_type,
            workflow_to_run_id=obj.workflow_to_run_id.to_json_str(),
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            commit_at=obj.commit_at,
            object_type_name=obj.object_type_name
        )

    @classmethod
    def from_db_row(cls, row: Dict) -> "WorkflowTriggerRecord":
        return WorkflowTriggerRecord(
            id=row["id"],
            owner_id=row["owner_id"],
            workflow_trigger_object_type_name=row["workflow_trigger_object_type_name"],
            workflow_trigger_event_type=row.get("workflow_trigger_event_type", ""),
            workflow_to_run_id=row.get("workflow_to_run_id", ""),
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
        query = f"INSERT INTO {WorkflowTriggerRecord.table_name()} ({WorkflowTriggerRecord.table_fields()}) " \
                f"VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        logger.debug(f'Running SQL query "{query}"')
        cursor.execute(
            query,
            (self.id, self.owner_id, self.workflow_trigger_object_type_name, self.workflow_trigger_event_type,
             self.workflow_to_run_id, self.created_at, self.updated_at, self.commit_at, self.object_type_name)
        )
        conn.commit()

    def insert_or_replace_to_db(self, conn: Connection, cursor: Cursor):
        now = time.time()
        self.commit_at = now
        query = f"INSERT OR REPLACE INTO {WorkflowTriggerRecord.table_name()} ({WorkflowTriggerRecord.table_fields()}) " \
                f"VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        logger.debug(f'Running SQL query "{query}"')
        cursor.execute(
            query,
            (self.id, self.owner_id, self.workflow_trigger_object_type_name, self.workflow_trigger_event_type,
             self.workflow_to_run_id, self.created_at, self.updated_at, self.commit_at, self.object_type_name)
        )
        conn.commit()

    def read_from_db_row(self, row: Dict[str, Any]) -> None:
        self.id = str(row["id"])
        self.owner_id = str(row["owner_id"])
        self.workflow_trigger_object_type_name = row["workflow_trigger_object_type_name"]
        self.workflow_trigger_event_type = row.get("workflow_trigger_event_type", "")
        self.workflow_to_run_id = row.get("workflow_to_run_id", "")
        self.created_at = float(row["created_at"])
        self.updated_at = float(row["updated_at"])
        self.commit_at = float(row["commit_at"])
        self.object_type_name = row["object_type_name"]

    def read_from_object(self, obj: WorkflowTrigger) -> None:
        self.id = str(obj.id)
        self.owner_id = obj.owner_id.to_json_str()
        self.workflow_trigger_object_type_name = obj.workflow_trigger_object_type_name
        self.workflow_trigger_event_type = obj.workflow_trigger_event_type
        self.workflow_to_run_id = obj.workflow_to_run_id.to_json_str()
        self.created_at = obj.created_at
        self.updated_at = obj.updated_at
        self.commit_at = obj.commit_at
        self.object_type_name = obj.object_type_name

    def convert_to_object(self) -> WorkflowTrigger:
        obj: WorkflowTrigger = WorkflowTrigger(
            id=uuid.UUID(self.id),
            owner_id=ObjectReference.from_json_string(self.owner_id),
            workflow_trigger_object_type_name=self.workflow_trigger_object_type_name,
            workflow_trigger_event_type=self.workflow_trigger_event_type,
            workflow_to_run_id=ObjectReference.from_json_string(self.workflow_to_run_id),
            created_at=self.created_at,
            updated_at=self.updated_at,
            commit_at=self.commit_at,
            object_type_name=self.object_type_name
        )
        return obj
